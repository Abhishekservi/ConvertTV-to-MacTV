# Credits and provenance

**Project customization and assembly:** Abhishek Choudhary, with AI-assisted coding and documentation.

## Launcher

Based on [Ansub/tv-detox](https://github.com/Ansub/tv-detox), commit `e94a2de4a79a91ccd4772e3531af0c4a7cf909d0`. Copyright Ansub Khan; MIT license retained in `launcher/LICENSE` and the repository license.

Personal additions include the city-night background, corner credit, console tile and input selection, optional app-level welcome and packaging as MacTV Home. The upstream source supplies much of the launcher layout, app management, settings shortcuts and vendor input handling. The public launcher retains the original six streaming app defaults and adds PS5 and the AirPlay receiver; missing apps are skipped.

The city-night wallpaper was generated for this project with an image-generation tool. It is an imagined night scene combining New York/Paris-style buildings and lighting, not a documentary photograph. This project distributes that generated image under the repository's MIT terms. No Apple product artwork is bundled. The public console tile is drawn in code; Sony's downloaded PS5 logo used privately on the reference TV is not included.

## Receiver

Based on [jqssun/android-airplay-server](https://github.com/jqssun/android-airplay-server), commit `a46cca0a6a1274e9e33c0e750f0f1c1eb1d881ea`, version 0.0.36, GPL-3.0. See `airplay/LICENSE` and `airplay/UPSTREAM-README.md`.

The original receiver developers implemented the Android AirPlay application and integrated the UxPlay engine. This project changes its application ID, personal names, color palette, 32-bit target, default frame-rate/startup/background settings and pins the OpenSSL source checksum. It does not claim to have invented or independently rewritten AirPlay.

## Names

Apple, AirPlay, Mac, MacBook, Apple TV, PlayStation, PS5 and the named streaming services are their respective owners' marks. Their use here describes compatibility, app shortcuts and the project goal; it does not imply endorsement or certification.
