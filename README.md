# ConvertTV to MacTV

**Give an Android TV a clean city-night home screen and configure free AirPlay screen mirroring from an iPhone or MacBook.**

Created and customized by **Abhishek Choudhary**, using the open-source TV Detox launcher and Android AirPlay Server/UxPlay projects. “MacTV” is a project nickname: the TV continues to run Android. This is an independent project, not an Apple product or an Apple-certified AirPlay receiver.

![City-night wallpaper](launcher/app/src/main/assets/city-lights.png)

## What you get

- A lightweight launcher with a city-night background, app tiles, HDMI shortcuts, a configurable PS5 tile and a personal corner credit.
- A separate free AirPlay receiver with a dark blue interface, screen mirroring and audio.
- Buildable source, pinned native dependencies, step-by-step iPhone/Mac instructions and troubleshooting.
- Inspection and setup helpers that default to dry-run, ask before each change and record undo actions **before** executing them.
- Optional animation and sleep tuning. Existing apps stay installed; the helpers never debloat or disable a stock launcher.

## Tested and untested

| Item | Status |
| --- | --- |
| Haier `haierATV`, Android 11, 32-bit ARM | Reference device |
| Android-reported app display mode | 1920 × 1080 at 60 Hz |
| Custom AirPlay APK | Compiled, signed and installed; user confirmed iPhone picture **and sound** |
| Original city launcher / PS5 HDMI switching | Worked on the reference TV |
| Public generalized launcher | Build checked; per-TV HDMI selection still needs device testing |
| MacBook mirroring | Instructions included; not confirmed on the reference TV |
| 60 fps | Available as an advisory setting; **not measured or confirmed** |
| 120 fps / 4K output | Not claimed; the reference TV exposed only 1080p/60 to Android apps |
| Welcome animation | Optional, off by default; experimental and not confirmed on the TV |

Actual streaming resolution and frame rate depend on the sender, decoder and network. Changing an advertised limit does not guarantee the sender will use it. No speed or memory gain is guaranteed.

## Before you begin

Turning off system apps has risk: some TVs have become stuck at the logo or kept restarting after debloating. AI-assisted instructions can contain mistakes. Keep a working original Home screen and an undo record. Undo can reverse recorded software changes **only if the TV remains reachable**; it cannot guarantee recovery from a boot failure.

This project's helpers **do not disable system apps**. Leave Google Play services, Play Store, Settings, System UI, setup, keyboard, Bluetooth, casting/voice/remote services, HDMI/input/tuner frameworks and all boot-critical or uncertain components enabled. On Google TV/Chromecast, also keep `com.google.android.apps.tv.launcherx` enabled. See [Safety and recovery](docs/SAFETY.md).

## End-to-end setup

1. **Prepare the TV and computer:** install Google's Platform Tools, enable debugging temporarily, connect on the same trusted network and approve the TV's prompt. A TV exposing only USB debugging may need an initial USB connection; do not assume Wi-Fi ADB is available. [Connection guide](docs/SETUP.md#1-connect-and-authorize).
2. **Inspect before changing anything:** save memory, display mode and installed/disabled package lists locally. Review every app; treat unknown apps as needed.
3. **Build the apps:** clone with submodules, install the listed Android SDK tools and run the build commands below. [Build guide](docs/BUILD.md).
4. **Install and preview separately:** the helper asks for each install and checks the APK's app ID. Keep the original Home enabled. Choose the default Home only after the preview works.
5. **Configure AirPlay:** open the receiver and choose **Start**. Connect an iPhone or Mac. Decide separately whether you want it to stay available while the Home screen is showing. [AirPlay guide](docs/AIRPLAY.md).
6. **Optional tuning:** turn off animations or set sleep to five minutes, with a separate confirmation and backup for each setting. Keep the screensaver enabled, especially if the TV might be OLED.
7. **Verify and finish:** test Home, remote, sound, casting, voice, phone remote and every HDMI input you use. If you choose a restart check, wait 30 seconds after the last change, restart once and verify normal startup. Disable debugging afterward.

### Get and build the source

```sh
git clone --recurse-submodules https://github.com/Abhishekservi/ConvertTV-to-MacTV.git
cd ConvertTV-to-MacTV

# Set JAVA_HOME and ANDROID_HOME first; see docs/BUILD.md.
./scripts/build.sh launcher debug
./scripts/build.sh airplay debug
```

The GitHub “Download ZIP” archive does **not** contain Git submodules. Use a recursive clone to build the AirPlay engine. Both apps are independent Android projects; the Gradle wrapper lives in `airplay/` and is shared by the build helper.

### Inspect, then install

Replace `TV_IP:PORT` with the endpoint shown by your TV. Do not paste the placeholder literally. `--apply` enables changes but **does not skip the individual prompts**.

```sh
python3 scripts/tv.py --tv TV_IP:PORT inspect

# First review the dry-run, then repeat with --apply before the subcommand.
python3 scripts/tv.py --tv TV_IP:PORT install --app airplay \
  --apk airplay/app/build/outputs/apk/debug/app-debug.apk
python3 scripts/tv.py --tv TV_IP:PORT --apply install --app airplay \
  --apk airplay/app/build/outputs/apk/debug/app-debug.apk
python3 scripts/tv.py --tv TV_IP:PORT --apply preview --app airplay
```

On the TV choose **Start**. On iPhone: **Control Center → Screen Mirroring → Abhishek’s TV**. On Mac: **Control Centre → Screen Mirroring → Abhishek’s TV**. Both devices must share a local network that permits discovery.

### Receiver configuration

```sh
# Each changed preference gets its own confirmation and undo record.
python3 scripts/tv.py --tv TV_IP:PORT --apply configure-airplay \
  --name "MacTV" --fps 30 --resolution auto --background off

# Optional: keep receiving while Home is displayed. Uses background resources.
python3 scripts/tv.py --tv TV_IP:PORT --apply configure-airplay --background on
```

The app defaults to a 30 fps advisory limit, automatic resolution, no automatic start at app launch, no boot startup and no background running. For a 60 fps experiment, use `--fps 60`, reconnect the sender and test motion and sound. Keep 30 fps if it stutters. There is no promise of 120 fps or a higher-resolution panel.

### Undo

```sh
python3 scripts/tv.py --tv TV_IP:PORT undo          # preview recorded reversals
./scripts/undo.sh --tv TV_IP:PORT --apply          # asks before every reversal
```

Backups are stored in the ignored `backups/` directory. Keep them outside GitHub and retain the same `--state-dir` if you choose a custom location. Undo restores recorded preferences/settings and the original Home before disabling project apps. Added apps stay installed. It never turns previously disabled unrelated apps back on.

## Limitations

- DRM-protected video such as Apple TV app playback is unsupported by the receiver. Use native TV streaming apps for protected content.
- Wi-Fi mirroring has latency and can stutter; it is not a replacement for a direct HDMI connection for gaming.
- TV firmware differs. Some vendors ignore the default-Home command. This project stops rather than disabling the stock launcher.
- The build targets `armeabi-v7a` to match the reference Haier. Other devices may need another ABI; see the build guide.
- The public launcher uses an original generic console tile. Sony's downloaded logo from the private setup is not redistributed.

## Source, credits and licenses

- Launcher: derived from [Ansub/tv-detox](https://github.com/Ansub/tv-detox), MIT; original copyright retained.
- AirPlay app: derived from [jqssun/android-airplay-server](https://github.com/jqssun/android-airplay-server), GPL-3.0; includes [UxPlay](https://github.com/FDH2/UxPlay) and other separately licensed native dependencies.
- Setup scripts and project documentation: MIT. The generated city wallpaper is included with this project; see [credits](docs/CREDITS.md).

See [build instructions](docs/BUILD.md), [setup](docs/SETUP.md), [AirPlay](docs/AIRPLAY.md), [safety](docs/SAFETY.md), [reference results](docs/REFERENCE-DEVICE.md), [local validation](docs/VALIDATION.md) and [third-party notices](THIRD_PARTY_NOTICES.md).

Do not publish device inventories, LAN addresses, screenshots of mirrored private content, logs, signing keys or credentials. They are excluded from this public project.
