# Reference device and actual results

The original project was developed on a Haier TV reporting the generic model `haierATV`, Android 11 / API 30, with `armeabi-v7a` app support and about 1.35 GiB of system RAM. Android exposed one app display mode: 1920 × 1080 at approximately 60 Hz. This is an Android display report, not an independent panel specification or proof of other HDMI modes.

## Confirmed

- The original customized city-night Home displayed seven main tiles: six streaming apps and a PS5 shortcut.
- The user confirmed the PS5 picture appeared when selecting its main tile. On that device the console was on HDMI 4. The public source asks for the input instead of hardcoding it.
- Two specifically approved restart checks completed successfully during the original appearance setup. Later small updates were checked without another restart at the user's request.
- A separate custom AirPlay receiver was release-built and installed. Its native engine started on port 7000 and registered the AirPlay/RAOP discovery services.
- The user confirmed iPhone picture and sound **both worked** through the receiver.
- All 134 original packages remained installed. Background running and both automatic startup options were off.

## Important gaps

- The later optional welcome preview was not confirmed. It stays off by default. The public source adjusts its animation clock to start at the first frame, but that public variant has not been installed on the reference TV.
- The public launcher has a new app ID, a generic console graphic and a configurable HDMI picker. It is a reusable source variant, not a claim that the exact published launcher APK ran on that TV.
- Casting through the independent receiver worked; the original Google Cast, voice-search and phone-remote end-to-end tests were not all confirmed by the user.
- MacBook mirroring was described but not confirmed.
- The receiver remained configured at 30 fps / auto resolution. The later 60/120 fps request was inspected but no higher-rate setting was approved/applied or measured.

## Memory observations

The original cleanup snapshot showed about 389.6 MiB MemAvailable; a later completed cleanup/restart snapshot showed about 536.6 MiB. When switching from the existing AirScreen process to the custom receiver in a later session, MemAvailable snapshots were about 515.4 and 662.2 MiB (MemFree 123.6 and 222.5 MiB).

These samples were taken under different process/cache conditions. They do not isolate a cause, establish a benchmark or guarantee a speed improvement. No raw private package inventory, network address or device log is published here.
