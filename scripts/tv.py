#!/usr/bin/env python3
"""Explicit, reversible Android TV setup. No third-party Python packages required."""
import argparse
import hashlib
import ipaddress
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent.parent
AIRPLAY = 'local.tv.airplay'
HOME = 'local.mactv.home'
ACTIVITY = {'airplay': AIRPLAY + '/io.github.jqssun.airplay.MainActivity',
            'launcher': HOME + '/local.tv.home.MainActivity'}
RECEIVER = AIRPLAY + '/io.github.jqssun.airplay.SettingsReceiver'
ACTION = 'io.github.jqssun.airplay.'
ADDED_APPS = {AIRPLAY, HOME}
TUNING = {('global', 'window_animation_scale'), ('global', 'transition_animation_scale'),
          ('global', 'animator_duration_scale'), ('secure', 'sleep_timeout')}
PREF_KEYS = {'server_name', 'max_fps', 'resolution', 'run_in_background'}


def endpoint(value):
    host, sep, port = value.partition(':')
    ipaddress.IPv4Address(host)
    if not sep:
        port = '5555'
    if not port.isdigit() or not 1 <= int(port) <= 65535:
        raise argparse.ArgumentTypeError('Use an IPv4 address and valid ADB port.')
    return host + ':' + port


class Adb:
    def __init__(self, executable, tv):
        self.executable, self.tv = executable, tv

    def run(self, *args):
        result = subprocess.run([self.executable, '-s', self.tv, *args], capture_output=True,
                                text=True, timeout=60)
        if result.returncode:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip() or 'ADB command failed')
        return result.stdout.replace('\r', '').strip()

    def shell(self, *args):
        # ADB reconstructs a remote shell command; quote every argument for that shell.
        return self.run('shell', shlex.join(str(a) for a in args))

    def connected(self):
        if self.run('get-state') != 'device':
            raise RuntimeError('TV is not authorized. Connect with adb and select Allow on the TV.')


class Setup:
    def __init__(self, adb, directory, apply=False, prompt=input):
        self.adb, self.directory, self.apply, self.prompt = adb, Path(directory), apply, prompt
        self.ledger = self.directory / 'undo.json'

    def load(self):
        if not self.ledger.exists():
            return {'tv': self.adb.tv, 'actions': []}
        data = json.loads(self.ledger.read_text())
        if data.get('tv') != self.adb.tv:
            raise RuntimeError('This backup belongs to another TV. Choose a separate --state-dir.')
        return data

    def save(self, data):
        self.directory.mkdir(parents=True, exist_ok=True)
        temp = self.ledger.with_suffix('.tmp')
        temp.write_text(json.dumps(data, indent=2) + '\n')
        temp.replace(self.ledger)

    def record(self, action):
        data = self.load()
        action = dict(action, recorded_at=int(time.time()))
        data['actions'].append(action)
        self.save(data)  # Persist BEFORE touching the device.

    def confirm(self, description):
        if not self.apply:
            print('DRY RUN: ' + description)
            return False
        return self.prompt(description + '\nType yes to approve this change: ').strip().lower() == 'yes'

    def present(self, package):
        # Unlike `pm path`, listing an absent package succeeds with empty output.
        packages = self.adb.shell('pm', 'list', 'packages', '--user', '0', package).splitlines()
        return 'package:' + package in packages

    def prefs(self):
        result = self.adb.shell('am', 'broadcast', '-n', RECEIVER, '-a', ACTION + 'LIST_SETTINGS')
        match = re.search(r'data="(\{.*\})"\s*$', result, re.S)
        if not match:
            raise RuntimeError('Could not read receiver preferences. Install/open the receiver first.')
        return json.loads(match.group(1))

    def put_pref(self, key, value):
        if key not in PREF_KEYS:
            raise RuntimeError('Unrecognized receiver preference; refusing to change it.')
        result = self.adb.shell('am', 'broadcast', '-n', RECEIVER, '-a', ACTION + 'SET_SETTING',
                                '--es', 'key', key, '--es', 'value', str(value).lower() if isinstance(value, bool) else str(value))
        if 'result=-1' not in result:
            raise RuntimeError('Receiver rejected the preference: ' + result)
        if str(self.prefs()[key]['value']).lower() != str(value).lower():
            raise RuntimeError('Receiver preference verification failed.')

    def configure(self, changes):
        before = self.prefs()
        for key, value in changes.items():
            old = before[key]['value']
            if str(old).lower() == str(value).lower():
                print(key + ': already set')
                continue
            if self.confirm(f'Change receiver {key} from {old!r} to {value!r}? A running cast may reconnect.'):
                self.record({'kind': 'preference', 'key': key, 'old': old})
                self.put_pref(key, value)

    def install(self, apk, package):
        if package not in ADDED_APPS:
            raise RuntimeError('Only this project’s two app IDs may be installed by this helper.')
        if self.present(package):
            raise RuntimeError('Package already installed. Helper refuses updates because it cannot undo an APK upgrade.')
        if not Path(apk).is_file():
            raise RuntimeError('APK file not found.')
        # Check the package using the Android SDK tool before install; do not trust a filename.
        sdk = __import__('os').environ.get('ANDROID_HOME', '')
        candidates = sorted((Path(sdk) / 'build-tools').glob('*/aapt2')) if sdk else []
        if not candidates:
            raise RuntimeError('Set ANDROID_HOME to an SDK with build-tools/aapt2 for APK identity checking.')
        metadata = subprocess.run([str(candidates[-1]), 'dump', 'badging', str(apk)],
                                  check=True, capture_output=True, text=True, timeout=15).stdout
        if not re.search(r"package: name='" + re.escape(package) + r"'", metadata):
            raise RuntimeError('APK package does not match the selected project app.')
        digest = hashlib.sha256(Path(apk).read_bytes()).hexdigest()
        if self.confirm(f'Install {package} from {apk}? SHA-256: {digest}. Undo disables it; nothing is uninstalled.'):
            self.record({'kind': 'new_app', 'package': package})
            result = self.adb.run('install', '--no-incremental', str(Path(apk).resolve()))
            if 'Success' not in result or not self.present(package):
                raise RuntimeError('Installation could not be verified: ' + result)

    def preview(self, app):
        if self.confirm('Open ' + app + ' for a preview? This does not change the default Home.'):
            self.adb.shell('am', 'start', '-W', '-n', ACTIVITY[app])
            print('For AirPlay, choose Start with the remote. Keep the app open unless background running is enabled.')

    def home(self):
        old = self.adb.shell('cmd', 'package', 'resolve-activity', '--brief', '-a',
                             'android.intent.action.MAIN', '-c', 'android.intent.category.HOME').splitlines()[-1]
        if old == ACTIVITY['launcher']:
            print('MacTV Home is already selected.')
            return
        if '/' not in old or old.startswith(('android/', 'com.android.internal.')):
            raise RuntimeError('Cannot identify an original Home component for undo. Use the TV settings instead.')
        if not self.present(HOME):
            raise RuntimeError('Install and preview MacTV Home first.')
        if self.confirm('Have you verified the preview? Make MacTV Home the default? All stock launchers stay enabled.'):
            self.record({'kind': 'home', 'old': old})
            self.set_home(ACTIVITY['launcher'])

    def set_home(self, component):
        # Never disables a stock launcher, even on firmware that ignores this command.
        self.adb.shell('cmd', 'package', 'set-home-activity', '--user', '0', component)
        actual = self.adb.shell('cmd', 'package', 'resolve-activity', '--brief', '-a',
                               'android.intent.action.MAIN', '-c', 'android.intent.category.HOME').splitlines()[-1]
        if actual != component:
            raise RuntimeError('Default Home routing was not verified. Stock Home stays enabled; use the saved undo record.')

    def tune(self, animations=False, sleep=None):
        changes = []
        if animations:
            changes += [('global', k, '0') for k in
                        ['window_animation_scale', 'transition_animation_scale', 'animator_duration_scale']]
        if sleep is not None:
            changes.append(('secure', 'sleep_timeout', str(sleep * 60000)))
        for scope, key, value in changes:
            old = self.adb.shell('settings', 'get', scope, key)
            if old == value:
                continue
            if self.confirm(f'Set {scope}/{key} from {old!r} to {value!r}? Screensaver settings stay unchanged.'):
                self.record({'kind': 'setting', 'scope': scope, 'key': key, 'old': old})
                self.put_setting(scope, key, value)

    def put_setting(self, scope, key, value):
        if (scope, key) not in TUNING:
            raise RuntimeError('Setting is outside the tuning allowlist.')
        if value == 'null':
            self.adb.shell('settings', 'delete', scope, key)
        else:
            self.adb.shell('settings', 'put', scope, key, value)
        if self.adb.shell('settings', 'get', scope, key) != value:
            raise RuntimeError('Setting restoration/change could not be verified.')

    def undo(self):
        data = self.load()
        for action in reversed(data['actions']):
            if action.get('undone'):
                continue
            if not self.confirm('Undo this recorded change: ' + json.dumps(action, ensure_ascii=False)):
                # Do not disable an added Home app after declining its original Home restoration.
                print('Undo stopped. Remaining records are retained.')
                return
            kind = action['kind']
            if kind == 'home':
                self.set_home(action['old'])
            elif kind == 'preference':
                if self.present(AIRPLAY):
                    self.put_pref(action['key'], action['old'])
            elif kind == 'setting':
                self.put_setting(action['scope'], action['key'], action['old'])
            elif kind == 'new_app':
                package = action['package']
                if package not in ADDED_APPS:
                    raise RuntimeError('Undo refuses to disable non-project apps.')
                if self.present(package):
                    if package == HOME:
                        selected = self.adb.shell('cmd', 'package', 'resolve-activity', '--brief', '-a',
                                                  'android.intent.action.MAIN', '-c', 'android.intent.category.HOME')
                        if selected.splitlines()[-1].startswith(HOME + '/'):
                            raise RuntimeError('Restore another Home before disabling MacTV Home.')
                    self.adb.shell('am', 'force-stop', package)
                    self.adb.shell('pm', 'disable-user', '--user', '0', package)
                    disabled = self.adb.shell('pm', 'list', 'packages', '-d', '--user', '0', package).splitlines()
                    if 'package:' + package not in disabled:
                        raise RuntimeError('Could not verify the added app was disabled.')
            else:
                raise RuntimeError('Unknown undo record. No further actions performed.')
            action['undone'] = True
            self.save(data)

    def inspect(self):
        report = {'model': self.adb.shell('getprop', 'ro.product.model'),
                  'android': self.adb.shell('getprop', 'ro.build.version.release'),
                  'abi': self.adb.shell('getprop', 'ro.product.cpu.abilist'),
                  'memory': self.adb.shell('cat', '/proc/meminfo'),
                  'storage': self.adb.shell('df', '-k', '/data'),
                  'display': self.adb.shell('dumpsys', 'display'),
                  'packages': self.adb.shell('pm', 'list', 'packages', '-f'),
                  'disabled_packages': self.adb.shell('pm', 'list', 'packages', '-d')}
        self.directory.mkdir(parents=True, exist_ok=True)
        name = self.directory / ('inspection-' + str(time.time_ns()) + '.json')
        name.write_text(json.dumps(report, indent=2) + '\n')
        print('Saved read-only inspection locally:', name)
        print('Model:', report['model'], '| Android:', report['android'], '| ABI:', report['abi'])
        print('\n'.join(l for l in report['memory'].splitlines() if l.startswith(('MemTotal:', 'MemFree:', 'MemAvailable:'))))
        print('Review every package before any separate manual cleanup. Unknown apps stay on.')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tv', required=True, type=endpoint, help='TV IPv4 address with optional ADB port')
    parser.add_argument('--adb', default='adb', help='Path to Google platform-tools adb')
    parser.add_argument('--state-dir', type=Path, help='Private local backup folder; never commit it')
    parser.add_argument('--apply', action='store_true', help='Enable changes; still asks before each one')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('inspect')
    install = sub.add_parser('install')
    install.add_argument('--app', choices=ACTIVITY, required=True)
    install.add_argument('--apk', type=Path, required=True)
    preview = sub.add_parser('preview'); preview.add_argument('--app', choices=ACTIVITY, required=True)
    cfg = sub.add_parser('configure-airplay')
    cfg.add_argument('--name'); cfg.add_argument('--fps', type=int, choices=[30, 60])
    cfg.add_argument('--resolution', choices=['auto', '1280x720', '1920x1080'])
    cfg.add_argument('--background', choices=['on', 'off'])
    sub.add_parser('home')
    tune = sub.add_parser('tune'); tune.add_argument('--animations-off', action='store_true')
    tune.add_argument('--sleep-minutes', type=int, choices=range(1, 121))
    sub.add_parser('undo')
    args = parser.parse_args(argv)
    state = args.state_dir or ROOT / 'backups' / args.tv.replace(':', '_')
    adb = Adb(args.adb, args.tv); adb.connected()
    setup = Setup(adb, state, args.apply)
    setup.load()  # Reject another TV's ledger before any action.
    if args.command == 'inspect': setup.inspect()
    elif args.command == 'install': setup.install(args.apk, AIRPLAY if args.app == 'airplay' else HOME)
    elif args.command == 'preview': setup.preview(args.app)
    elif args.command == 'home': setup.home()
    elif args.command == 'tune': setup.tune(args.animations_off, args.sleep_minutes)
    elif args.command == 'undo': setup.undo()
    elif args.command == 'configure-airplay':
        changes = {k: v for k, v in [('server_name', args.name), ('max_fps', args.fps), ('resolution', args.resolution)] if v is not None}
        if args.background is not None: changes['run_in_background'] = args.background == 'on'
        setup.configure(changes)
    print('When finished testing, turn off USB, Network and Wireless debugging on the TV.')


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError, ValueError, subprocess.SubprocessError, KeyboardInterrupt) as error:
        print('Stopped:', error, file=sys.stderr)
        sys.exit(1)
