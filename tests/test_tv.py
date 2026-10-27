"""Exercise reversible setup using a fake device. Never connects to a TV."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('tv', Path(__file__).resolve().parents[1] / 'scripts/tv.py')
tv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tv)


class Device:
    tv = '198.51.100.20:5555'  # Reserved documentation address, not a private device.

    def __init__(self):
        self.calls = []
        self.home = 'com.vendor.home/.MainActivity'
        self.apps = {tv.HOME, tv.AIRPLAY}
        self.disabled = set()
        self.settings = {('secure', 'sleep_timeout'): 'null',
                         ('global', 'window_animation_scale'): '0.5',
                         ('global', 'transition_animation_scale'): '0.5',
                         ('global', 'animator_duration_scale'): '0.5'}
        self.preferences = {'server_name': 'TV', 'max_fps': 30, 'resolution': 'auto', 'run_in_background': False}
        self.before_mutation = lambda: None
        self.fail_home = False

    def shell(self, *args):
        self.calls.append(args)
        if args[:2] == ('pm', 'path'):
            return 'package:/data/app/base.apk' if args[2] in self.apps else ''
        if args[:3] == ('cmd', 'package', 'resolve-activity'):
            return 'priority=0\n' + self.home
        if args[:3] == ('cmd', 'package', 'set-home-activity'):
            if not self.fail_home: self.home = args[-1]
            return 'Success'
        if args[:2] == ('settings', 'get'):
            return self.settings.get((args[2], args[3]), 'null')
        if args[:2] == ('settings', 'put'):
            self.before_mutation()
            self.settings[(args[2], args[3])] = args[4]
            return ''
        if args[:2] == ('settings', 'delete'):
            self.settings.pop((args[2], args[3]), None)
            return ''
        if args[:2] == ('am', 'broadcast'):
            if tv.ACTION + 'LIST_SETTINGS' in args:
                return 'Broadcast completed: result=-1, data="' + json.dumps({k: {'value': v} for k, v in self.preferences.items()}) + '"'
            key = args[args.index('key') + 1]
            value = args[args.index('value') + 1]
            if isinstance(self.preferences[key], bool):
                if value not in ('true', 'false'): return 'Broadcast completed: result=0'
                value = value == 'true'
            elif isinstance(self.preferences[key], int): value = int(value)
            self.preferences[key] = value
            return 'Broadcast completed: result=-1'
        if args[:2] == ('pm', 'disable-user'):
            self.disabled.add(args[-1]); return 'disabled-user'
        if args[:3] == ('pm', 'list', 'packages'):
            source = self.disabled if '-d' in args else self.apps
            return '\n'.join('package:' + p for p in source if args[-1] in p)
        return ''


class Reversibility(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.device = Device()
        self.setup = tv.Setup(self.device, self.temp.name, apply=True, prompt=lambda _: 'yes')

    def test_dry_run_does_not_write_or_mutate(self):
        self.setup.apply = False
        self.setup.tune(animations=True, sleep=5)
        self.assertFalse(self.setup.ledger.exists())
        self.assertFalse(any(c[:2] == ('settings', 'put') for c in self.device.calls))

    def test_declining_one_setting_makes_no_change(self):
        self.setup.prompt = lambda _: 'no'
        self.setup.tune(sleep=5)
        self.assertFalse(self.setup.ledger.exists())
        self.assertEqual(self.device.settings[('secure', 'sleep_timeout')], 'null')

    def test_original_is_saved_before_mutation(self):
        def before():
            action = json.loads(self.setup.ledger.read_text())['actions'][-1]
            self.assertEqual(action['old'], 'null')
            self.assertEqual(action['key'], 'sleep_timeout')
        self.device.before_mutation = before
        self.setup.tune(sleep=5)
        self.assertEqual(self.device.settings[('secure', 'sleep_timeout')], '300000')

    def test_absent_setting_is_deleted_on_undo(self):
        self.setup.tune(sleep=5)
        self.setup.undo()
        self.assertNotIn(('secure', 'sleep_timeout'), self.device.settings)

    def test_background_boolean_round_trip(self):
        self.setup.configure({'run_in_background': True})
        self.assertTrue(self.device.preferences['run_in_background'])
        self.setup.undo()
        self.assertFalse(self.device.preferences['run_in_background'])

    def test_repeated_preference_changes_undo_in_reverse_order(self):
        self.setup.configure({'max_fps': 60})
        self.setup.configure({'max_fps': 30})
        self.setup.undo()
        self.assertEqual(self.device.preferences['max_fps'], 30)
        writes = [c[c.index('value') + 1] for c in self.device.calls
                  if c[:2] == ('am', 'broadcast') and tv.ACTION + 'SET_SETTING' in c]
        self.assertEqual(writes, ['60', '30', '60', '30'])

    def test_undo_restores_home_before_disabling_added_launcher(self):
        self.setup.record({'kind': 'new_app', 'package': tv.HOME})
        self.setup.home()
        self.setup.undo()
        self.assertEqual(self.device.home, 'com.vendor.home/.MainActivity')
        self.assertIn(tv.HOME, self.device.disabled)
        restore = next(i for i, c in enumerate(self.device.calls)
                       if c[:3] == ('cmd', 'package', 'set-home-activity') and c[-1] == 'com.vendor.home/.MainActivity')
        disable = next(i for i, c in enumerate(self.device.calls) if c[:2] == ('pm', 'disable-user'))
        self.assertLess(restore, disable)

    def test_failed_home_restore_does_not_disable_launcher(self):
        self.setup.record({'kind': 'new_app', 'package': tv.HOME})
        self.setup.home()
        self.device.fail_home = True
        with self.assertRaises(RuntimeError): self.setup.undo()
        self.assertNotIn(tv.HOME, self.device.disabled)

    def test_declining_home_restore_stops_undo(self):
        self.setup.record({'kind': 'new_app', 'package': tv.HOME})
        self.setup.home()
        self.setup.prompt = lambda _: 'no'
        self.setup.undo()
        self.assertFalse(self.device.disabled)

    def test_no_system_app_can_be_disabled_by_undo(self):
        self.setup.record({'kind': 'new_app', 'package': 'com.google.android.gms'})
        with self.assertRaises(RuntimeError): self.setup.undo()
        self.assertFalse(self.device.disabled)

    def test_setting_allowlist_rejects_unrelated_changes(self):
        with self.assertRaises(RuntimeError): self.setup.put_setting('secure', 'screensaver_enabled', '0')
        self.assertFalse(self.device.calls)

    def test_preference_allowlist_rejects_unrelated_changes(self):
        with self.assertRaises(RuntimeError): self.setup.put_pref('boot_auto_start', 'true')
        self.assertFalse(self.device.calls)

    def test_cannot_reuse_another_tvs_ledger(self):
        self.setup.record({'kind': 'new_app', 'package': tv.AIRPLAY})
        self.device.tv = '198.51.100.21:5555'
        with self.assertRaises(RuntimeError): self.setup.load()

    def test_finished_undo_actions_are_not_repeated(self):
        self.setup.tune(sleep=5)
        self.setup.undo()
        count = len(self.device.calls)
        self.setup.undo()
        self.assertEqual(count, len(self.device.calls))

    def test_endpoint_validation(self):
        self.assertEqual(tv.endpoint('198.51.100.20'), '198.51.100.20:5555')
        with self.assertRaises(ValueError): tv.endpoint('198.51.100.20;echo bad')
        with self.assertRaises(Exception): tv.endpoint('198.51.100.20:0')

    def test_package_lookup_does_not_confuse_prefix_matches(self):
        self.device.apps.remove(tv.AIRPLAY)
        self.device.apps.add(tv.AIRPLAY + '.other')
        self.assertFalse(self.setup.present(tv.AIRPLAY))


if __name__ == '__main__':
    unittest.main()
