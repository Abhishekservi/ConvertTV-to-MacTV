# Third-party source and licenses

This is a mixed-license repository. The root MIT license covers the setup tools/documentation and MIT launcher-derived work; **it does not relicense the GPL AirPlay application**.

| Component | Source | License location |
| --- | --- | --- |
| TV Detox launcher | https://github.com/Ansub/tv-detox | `launcher/LICENSE` (MIT) |
| Android AirPlay Server | https://github.com/jqssun/android-airplay-server | `airplay/LICENSE` (GPL-3.0) |
| UxPlay | https://github.com/FDH2/UxPlay | Pinned submodule's `LICENSE*` / `COPYING*` and individual file notices |
| FFmpeg | https://github.com/FFmpeg/FFmpeg | Pinned submodule license files; minimal audio decoder build, with component terms retained |
| libplist | https://github.com/libimobiledevice/libplist | Pinned submodule's license/copyright notices |
| openssl-cmake | https://github.com/viaduck/openssl-cmake | Pinned submodule's `LICENSE` (MIT) |
| OpenSSL 3.4.4 | https://github.com/openssl/openssl/releases/tag/openssl-3.4.4 | Downloaded source's `LICENSE.txt` and notices (Apache-2.0) |

AndroidX, Kotlin/coroutines, Hilt/Dagger, Media3 and Oboe are declared in the receiver's Gradle dependency files. Their own licenses and bundled notices remain applicable. Gradle's wrapper and Android build tools retain their respective upstream terms; Android SDK binaries are not vendored here.

For an AirPlay binary distribution, preserve GPL source availability and notices: publish the matching source revision, its build scripts and pinned native dependency sources. A GitHub source ZIP omits submodule content; use a recursive clone, and include a full corresponding-source bundle if distributing binaries separately. Never substitute a private session backup or signing key for source.
