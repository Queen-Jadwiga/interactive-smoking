# Interactive Smoking — v0.9 beta

Interactive cigarette smoking for S.T.A.L.K.E.R. Anomaly / GAMMA, by Queen-Jadwiga.

## Branches

- **main**: runtime package plus development scripts, mocked checks and source notes.
- **end-user**: installable mod files and player documentation only. Players should download this branch or the v0.9 beta release.

See [player instructions](README_USER.md) for requirements, installation, controls, optional addons and limits.

## Accepted baseline

v0.9 promotes the user-tested **0.1.4** build. Runtime changes are version/label metadata only. Both OMF animation files and all three Ogg cues remain byte-identical. Later 0.1.5 activation diagnostics are not included. The October 15 user test log records three sessions, one pack use per session, exhale events at 2100–2116ms and clean stop reasons; no smoking-controller error was observed. User video confirms the accepted motion and ignition effect. Raw logs/video are not stored in this repository.

## Development

Python asset checks require NumPy, SciPy and FFmpeg/FFprobe; the controller fixture runs with texlua (Lua 5.3). Game code remains compatible with Lua 5.1 syntax. Obtain the source FDDA Redone assets separately; local workstation paths in historical source notes are evidence references, not distributed dependencies.

```sh
texlua development/controller_fixtures.lua .
python development/check_assets.py /path/to/FDDA-Redone/gamedata
python development/check_audio.py
python development/package_release.py /path/to/Interactive_Smoking_0.9_Beta.zip --end-user
```

See [source notes](development/SOURCE_NOTES.md) for engine/source evidence, development history and runtime limitations. Mocked and binary checks do not substitute for in-game testing. Cigars and other tobacco types are outside this beta.
