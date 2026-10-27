# Safety, undo and recovery

Turning off system apps can leave some TVs stuck at a logo or restarting. AI-assisted instructions can be wrong. This project avoids automatic debloating and keeps stock Home components enabled. Do not interpret “worked on one Haier” as proof for another TV or firmware.

## Protected components

Never disable Google Play services (`com.google.android.gms`), Google Play, Settings, System UI, setup apps, the active keyboard, Bluetooth, casting/voice/remote services, HDMI/input/tuner frameworks, boot-critical services or an uncertain vendor package. On Google TV/Chromecast keep `com.google.android.apps.tv.launcherx` enabled. OEM package names vary; this is a minimum list, not a complete safe/unsafe classifier.

Keep the screensaver enabled for an OLED panel or when the panel type is unknown. Backdrop may be the TV's active screensaver. Sleep tuning does not replace burn-in protection and is not a reason to disable it.

## What the helper may change

Only after an explicit per-action prompt with `--apply`:

- Install one of this project's two **new** apps, with APK app-ID verification.
- Open a project app for preview.
- Change receiver name, advertised FPS/resolution or background running.
- Select the added launcher as Home after recording the current component.
- Change three animation scales and Android's secure sleep timeout.

The helper has no command to disable or uninstall a system package, enable debugging, grant overlay permission, modify firmware, replace boot animations, turn off the screensaver or reboot the TV. A package upgrade is refused because installing a newer APK is not reversible with the stored preference ledger alone.

## Backups

`backups/<endpoint>/undo.json` is written **before** each mutation. It contains the target endpoint, originals and completed undo status. Read-only inspection reports contain package lists and device information. They remain local and are ignored by Git.

Keep this directory and the computer that has authorized debugging access available. Use the same `--state-dir` during undo if a custom directory was selected. Confirm you are targeting the correct TV; the helper rejects a ledger belonging to a different endpoint. If DHCP changes the TV's address, review the record yourself rather than editing it blindly or directing an old record at another device.

## Restore

```sh
./scripts/undo.sh --tv TV_IP:PORT --apply
```

Undo asks before each recorded reversal. It restores Home routing before disabling an added Home app, verifies applicable settings and app state, and marks completed actions so it can resume after interruption. If a Home restoration fails or you decline a reversal, it stops. Added apps stay installed and can be enabled again from the TV's Apps settings.

Undo restores changes made **through this helper**. It cannot reconstruct manual changes, restore an APK upgrade, repair firmware or guarantee recovery if Android cannot boot or ADB is no longer reachable. The original private session's backup is deliberately not bundled in this repository: it belongs to one specific TV.

## Debugging

After testing, turn off USB, Network and Wireless debugging, or Developer options. Do not forward debugging ports through a router or leave them exposed on public/shared networks. Turn debugging back on only when you need an authorized undo or update session.

If the TV cannot start, stop experimenting with package commands. Use the manufacturer's documented recovery/support procedure. Do not blindly disable more components, unlock a bootloader, remount protected partitions or factory-reset without considering the data loss.
