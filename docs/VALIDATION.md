# Publication preparation checks

Checked locally on 2026-10-27:

- Both projects compiled with assembleDebug: launcher and AirPlay, including the pinned native AirPlay dependencies.
- Both APK signatures and alignment verified.
- All 16 setup/recovery tests passed against a fake device. No TV connection is used by the tests.
- Python syntax, shell syntax, XML manifests and local documentation links checked.
- The tracked publication files were checked for private keys, credentials, personal email addresses, private device endpoints, inventories and raw logs.

The OpenSSL mirror download was interrupted once during validation. The build completed using an existing copy checked against the same pinned official SHA-256. If a source download is interrupted on another computer, verify network access and retry; do not remove checksum verification.

These public debug APKs have not been installed on the reference TV. The original locally release-signed AirPlay variant was the version the user tested successfully. The generalized launcher’s per-TV console picker and optional welcome need physical-device testing. See REFERENCE-DEVICE.md for the exact boundaries of the original results.

GitHub Actions has not run until the project is published. Its lightweight workflow validates the Python/shell setup tools; it does not build Android APKs or establish device compatibility.
