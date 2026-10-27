# Configure AirPlay from beginning to end

## Start the receiver

Open **Abhishek’s AirPlay** and choose **Start** with the TV remote. The overview should show **Waiting for connection**. The default receiver name is **Abhishek’s TV**; you can change it in Settings or with the helper.

Both devices must be on the same local network. Guest Wi-Fi, client isolation or some VPN configurations can prevent discovery even when both devices have internet access. Discovery uses the local `_airplay._tcp` and `_raop._tcp` services. Do not expose the receiver's ports to the internet.

If another receiver such as AirScreen is already running, stop that app's receiver/session before testing this one so it does not occupy the same ports. This is a separate change: ask the owner first, and do not remove the other app or alter its startup settings.

## iPhone / iPad

1. Open Control Center.
2. Choose **Screen Mirroring → Abhishek’s TV** (or your configured name).
3. If the receiver was configured to require a PIN, follow its displayed prompt. PIN mode is an upstream beta feature and was not tested in the reference setup.
4. Test your Home screen and a short personal video in Photos, including sound.
5. Choose **Stop Mirroring** when finished, then **Stop** in the TV receiver for a manual session.

iPhone full-screen mirroring uses AirPlay. Google Home is not the equivalent Android-style “cast entire screen” control on an iPhone. The existing Google Cast service remains useful for sender apps that have their own Cast button.

## MacBook / Mac

1. Start the receiver on the TV and keep it open.
2. On the Mac, open **Control Centre → Screen Mirroring**.
3. Choose **Abhishek’s TV**.
4. Choose a mirroring option if macOS offers mirror/extend choices. Display options vary by macOS and sender support; extended desktop support is not claimed for this build.
5. Test motion and sound. If audio remains on the Mac, check the Mac's sound output selection and the TV's mute/volume state.
6. Disconnect from Screen Mirroring when finished.

Apple's [Mac screen-sharing guide](https://support.apple.com/guide/mac-help/stream-content-to-apple-tv-mh40768/mac) describes the macOS controls. This independent receiver may behave differently from an Apple TV.

## Where is the app on the custom Home?

Use **Add app → Abhishek’s AirPlay**, then open its new tile. Newly installed apps do not necessarily appear in a saved custom tile list automatically. The public launcher's initial app list includes the receiver when it is installed.

### It worked, but disappeared after returning Home

Background running is off by default. When you leave an idle receiver, it stops listening. Reopen the app and choose Start, or separately approve background running:

```sh
python3 scripts/tv.py --tv TV_IP:PORT --apply configure-airplay --background on
```

Open/start the receiver once afterward. Keeping the service running after leaving the app does not automatically grant Android permission to bring its video screen to the foreground. On some firmware **Settings → Launch on connection** requires the user to approve “display over other apps”; the helper does not grant that permission. If a connection has sound but no visible video while Home is showing, open the receiver manually. A foreground connection is the tested workflow.

To return to manual sessions:

```sh
python3 scripts/tv.py --tv TV_IP:PORT --apply configure-airplay --background off
```

## Resolution and frame rate

Defaults: automatic resolution, 30 fps advertised maximum. On the reference Haier, Android reported 1920 × 1080 at 60 Hz. Auto resolution already requests that display size, subject to decoder limits; selecting explicit 1080p is not necessarily an upgrade.

```sh
# An optional experiment, not a verified performance claim.
python3 scripts/tv.py --tv TV_IP:PORT --apply configure-airplay \
  --fps 60 --resolution 1920x1080
```

Each preference is separately approved and saved for undo. A running receiver may restart its service when such preferences change; reconnect the sender. Start with a good local Wi-Fi connection or Ethernet on the TV if available. If motion or sound stutters, return to `--fps 30`, or try `--resolution 1280x720`.

UxPlay treats these values as **requests to the sender**. They do not force 60 fps, improve the source video's resolution, or create a 120 Hz TV panel. Neither actual 60 fps nor 4K/120 fps was verified in this project. Use the receiver's optional statistics overlay for measurement only if you choose to enable it; a configuration value alone is not evidence of the received rate.

## Other limits and troubleshooting

- Protected video such as Apple TV app playback is unsupported. Do not use a protected movie as the first test; use a personal Photos video. Native TV streaming apps remain the right route for DRM content.
- If the receiver is missing, verify it says Waiting for connection, both devices share the same local network, and guest isolation/VPN is not blocking discovery.
- If Start fails, check that another AirPlay app has stopped and that the TV has enough resources. Keep useful startup logs locally and redact device names/network details before sharing.
- No firmware, root, bootloader or real boot-animation change is part of AirPlay setup.
- Disable debugging after configuration and testing. Normal AirPlay use does not require ADB debugging to remain enabled.
