# Changelog

[Русская версия](CHANGELOG_ru.md)

## 2026-10-23

- First release of Split: a browser app (`index.html`) and a Python
  CLI (`split.py`).
- Four stems from HTDemucs — vocals, drums, bass, other — plus an
  instrumental built from drums, bass and other.
- Browser: MP3 or WAV output, a "First 30 s" check, per-stem players
  and downloads, a ZIP with everything, RU/EN toggle, the model cached
  in the browser after the first download.
- Browser engine adapted from demucs-web (MIT). Segments are now
  crossfaded across exactly the overlap, with no fade at the very start
  and end of the track.
- CLI: MP3 or WAV output, `htdemucs` and `htdemucs_ft`, folders and
  recursive search, `--overwrite`, `--no-instrumental`. Audio is read
  and written through ffmpeg, so no TorchAudio is needed.
