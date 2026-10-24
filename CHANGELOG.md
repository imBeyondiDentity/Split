# Changelog

[Русская версия](CHANGELOG_ru.md)

## 2026-10-24

- Added `split.ipynb`, a Google Colab notebook for phones: upload a
  track, get a ZIP with all five files, using `split.py` on a free GPU.
- On phones (and after a killed tab) the page shows a card with an
  "Open in Colab" button.
- `split.py` now sets `TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD` before
  importing PyTorch, because Demucs 4.0.1 checkpoints do not load under
  the PyTorch 2.6+ default.

## 2026-10-23

- Redesigned to match the shared MiSE look: cards with orange
  labels, filled segmented controls, version tag at the top left,
  EN/RU toggle at the top right, a footer with Github, the brand and
  Contact, and two columns on a wide screen. The language choice is
  remembered.
- Phone memory fixes: on phones the model runs on WASM only, with
  graph optimisation off, no kept copy of the model after loading and
  no cache copy. If a tab is killed during a run, the page now says so
  after it reloads, and a note about memory shows up on phones.
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
