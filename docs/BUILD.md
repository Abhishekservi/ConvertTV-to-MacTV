# Build both apps

## Requirements

- Git, Python 3.10+ and JDK 17+ (the reference build used JDK 17).
- Google's [Android SDK command-line tools](https://developer.android.com/studio#command-tools) and [Platform Tools](https://developer.android.com/tools/releases/platform-tools).
- For the launcher: Android platform 34 and Build Tools 36.0.0.
- For AirPlay: Android platform 37.0 (API 37), Build Tools 36.0.0, NDK `27.0.12077973`, CMake `3.22.1`, and host `make`/Perl/Python.
- The included Gradle wrapper uses **9.8.1**, pinned to its official SHA-256.

Set `JAVA_HOME` to your JDK and `ANDROID_HOME` to your SDK. Put the SDK's `platform-tools` directory on `PATH`. Avoid publishing SDK paths or `local.properties`.

Install the SDK packages using Android Studio or the official SDK manager, accepting the applicable SDK licenses yourself. Example package IDs:

```sh
sdkmanager "platform-tools" "platforms;android-34" "platforms;android-37.0" \
  "build-tools;36.0.0" "ndk;27.0.12077973" "cmake;3.22.1"
```

Tool availability/package naming can differ between SDK manager versions; use its package list if it reports an unknown ID. No APK can be built without downloading public Android dependencies on the first run.

## Clone the native dependencies

```sh
git clone --recurse-submodules https://github.com/Abhishekservi/ConvertTV-to-MacTV.git
cd ConvertTV-to-MacTV
git submodule update --init --recursive --depth 1
```

Pins:

| Dependency | Commit |
| --- | --- |
| UxPlay | `df67c212a433cf6dda3676dd40c097900d24e645` |
| FFmpeg | `38b88335f99e76ed89ff3c93f877fdefce736c13` |
| libplist | `f41b1ea67045e0c09339974d83e389972d84f166` |
| openssl-cmake | `4edd36a8dab5f85a8f92650b5bdf6e0cab13aab8` |

OpenSSL 3.4.4 is fetched during native compilation and checked against the pinned checksum in `airplay/app/src/main/cpp/CMakeLists.txt`. Preserve the upstream patch task: it restores and applies the required UxPlay patches before CMake configuration. Do not keep uncommitted personal edits in the patched UxPlay files; the upstream task resets those files.

## Compile

```sh
./scripts/build.sh launcher debug
./scripts/build.sh airplay debug
```

Outputs:

- `launcher/app/build/outputs/apk/debug/app-debug.apk` — package `local.mactv.home`.
- `airplay/app/build/outputs/apk/debug/app-debug.apk` — package `local.tv.airplay`.

Debug APKs use a local Android debug key. Keys are ignored by Git. Do not upload your signing key. Different builders' signatures may differ; Android rejects an in-place update signed with another key. The installer intentionally refuses to update an existing package, and never uninstalls it to work around a signature mismatch.

For a release build use `./scripts/build.sh airplay release`; the APK is unsigned unless you supply your own signing configuration. Follow Android's [app signing guide](https://developer.android.com/studio/publish/app-signing), keep the private key safe, and verify the finished APK with `apksigner verify` and `zipalign -c`. The receiver APK tested on the reference TV was locally release-signed; your newly built debug APK is a different signature.

## Other processors and branding

The reference receiver builds only `armeabi-v7a`. To build for a 64-bit TV, change `allAbis` in `airplay/app/build.gradle.kts` to include `arm64-v8a`. This broadens compilation targets; it does not guarantee device compatibility.

Customize:

- Launcher tiles: `launcher/app/src/main/java/local/tv/home/Apps.java`, or use **Add app** on the TV.
- Launcher labels, credit and app-level welcome: `MainActivity.java`.
- Wallpaper: `launcher/app/src/main/assets/city-lights.png`.
- Receiver app label: `airplay/app/src/main/res/values/strings.xml`.
- Default receiver name/startup/FPS: `airplay/.../Prefs.kt`, or use the configuration helper after installation.
- Dark receiver colors: `airplay/.../ui/theme/Theme.kt`.

The PS5 shortcut asks which HDMI input is connected on first selection. It saves the chosen ID within the added launcher only and leaves the TV's system input labels alone. The public launcher keeps its optional welcome off by default; its welcome and generalized HDMI picker are build-tested but not confirmed on the physical TV.

## Checks

```sh
python3 -m unittest discover -s tests -v
python3 -m py_compile scripts/tv.py
bash -n scripts/build.sh scripts/undo.sh
```

The lightweight GitHub workflow runs these helper checks. Android build success and actual device/sender tests are separate checks; a green helper workflow is not proof that mirroring works on every TV.
