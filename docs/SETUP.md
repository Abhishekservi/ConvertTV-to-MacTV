# End-to-end TV setup

## 1. Connect and authorize

Put the computer and TV on the same trusted home network. Find the TV's address under **Settings → Network → connected network**, or **About → Status**. Enable Developer options (often by selecting Build repeatedly), then enable the debugging option your TV actually offers. Menu names vary by firmware.

- **Wireless debugging with pairing:** use the TV's pairing address/port with `adb pair`, enter the displayed pairing code, then `adb connect` to its separate debugging address/port.
- **Network debugging:** use the TV's displayed endpoint and approve the computer on the TV.
- **USB debugging only:** do not assume enabling it opens port 5555. Use the manufacturer-supported USB debugging connection if available. Some TVs require a supported initial USB connection and `adb tcpip 5555`; some expose a network endpoint through their firmware. Avoid unsafe USB cable arrangements or service-menu changes. If you cannot establish authorized ADB, stop here.

```sh
adb connect TV_IP:PORT
adb devices -l
```

Select **Allow** on the TV's computer authorization prompt. `adb devices` must show `device`, not `unauthorized` or `offline`. The helper uses an already-authorized connection and does not enable debugging for you. Wake a sleeping TV with the remote. Do not reboot just to fix a stale connection; try disconnect/reconnect first.

## 2. Inspect before changing anything

```sh
python3 scripts/tv.py --tv TV_IP:PORT inspect
```

This reads model/Android/ABI, display modes, memory, storage, installed packages and disabled packages. It saves a private JSON report under ignored `backups/`. Do not upload it.

Review every app in plain language before a separate manual cleanup:

| Category | Examples and rule |
| --- | --- |
| Needed by the TV / uncertain | Google services, Store, Settings, System UI, setup, keyboard, remote, Bluetooth, inputs/tuner, screensaver and unknown vendor packages: leave enabled |
| Apps you use | Streaming services, casting, voice search, phone remote, HDMI/live TV: keep |
| Possible optional candidates | Printing, feedback or recommendation components: verify the exact TV/firmware and actual use first; no global safe-to-disable list |

This repository does not run a debloat list. On the reference Haier, Google Backdrop was the active screensaver and was kept even though a generic list elsewhere had described it as optional.

Record both **MemAvailable** and **MemFree** before/after. Available memory includes reclaimable caches; free memory alone is not a useful speed score. Compare equivalent usage conditions and do not promise a performance gain from one snapshot.

## 3. Install and preview

Build the APKs as described in [BUILD.md](BUILD.md). Run dry-runs first, then add `--apply` before the command to enable the individual prompts:

```sh
python3 scripts/tv.py --tv TV_IP:PORT --apply install --app launcher \
  --apk launcher/app/build/outputs/apk/debug/app-debug.apk
python3 scripts/tv.py --tv TV_IP:PORT --apply preview --app launcher
```

Use the remote. Check the app tiles, Settings, Back/Home behavior and every HDMI input you use. Missing streaming apps are skipped, not installed automatically; install them normally from Google Play. Choose **Add app** to add the receiver. On the PS5 tile's first selection choose the console's real HDMI input, power on the console and confirm its picture.

The separate AirPlay installation is another explicit approval:

```sh
python3 scripts/tv.py --tv TV_IP:PORT --apply install --app airplay \
  --apk airplay/app/build/outputs/apk/debug/app-debug.apk
python3 scripts/tv.py --tv TV_IP:PORT --apply preview --app airplay
```

## 4. Choose Home only after a working preview

```sh
python3 scripts/tv.py --tv TV_IP:PORT --apply home
```

The helper records the existing default Home, attempts the supported package-manager selection, then checks the actual resolved Home. It never disables a stock launcher. If firmware ignores the selection, the helper stops. Use the manufacturer's Home selection settings if available, or keep the stock Home. Do not disable setup, the Google TV launcher, or uncertain components to force a replacement.

## 5. Configure and test AirPlay

Follow [AIRPLAY.md](AIRPLAY.md). There is an intentional difference between these options:

- **Run in background:** after starting the receiver, keep it available when returning Home. This uses background memory/network resources. It does not enable boot startup.
- **Start server automatically:** starts receiving when the app opens.
- **Start server at boot:** starts receiving after Android starts.

The build defaults all three to off. The helper can separately change only background running; it does not silently enable boot startup. Keep the app open and choose Start for the simplest manual workflow.

## 6. Optional animation and sleep tuning

```sh
python3 scripts/tv.py --tv TV_IP:PORT --apply tune --animations-off --sleep-minutes 5
```

Each of the three animation scales and the sleep timeout receives its own prompt and a before-change record. Sleep is a request to Android's `secure/sleep_timeout`; vendor behavior may differ. It does not guarantee sleep during every kind of playback. Screensaver settings stay unchanged.

Ask whether the panel is OLED. If it is OLED or the user is unsure, keep the screensaver on. This helper never disables it. Do not conflate “no animations” with a faster decoder or processor.

## 7. Verify and finish

1. Re-run inspection and compare memory with the before report under similar usage.
2. Test Home, remote navigation, sound, iPhone casting, voice search, phone remote and your HDMI/live-TV inputs.
3. If you approve a restart check, wait at least 30 seconds after the last change, restart once and verify the TV reaches Home normally. The helper does **not** reboot automatically.
4. Disable USB, Network and Wireless debugging (or Developer options). Other devices on the network can request debugging access while it is exposed. Turn it back on only for your undo workflow or updates.

## 8. Undo

```sh
./scripts/undo.sh --tv TV_IP:PORT              # previews the next reversal and stops
./scripts/undo.sh --tv TV_IP:PORT --apply      # confirms each reversal
```

Use the same private backup directory. Undo proceeds in reverse order and records completed reversals so an interrupted run can resume. If original Home restoration fails or you decline it, undo stops before disabling the added Home app. For an added receiver it stops/disables the app; it does not remove it. No app data is deleted by these helpers.
