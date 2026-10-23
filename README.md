# Split

[![Licence: MIT](https://img.shields.io/badge/Licence-MIT-yellow.svg)](LICENSE)
[![Open Split](https://img.shields.io/badge/Open-Split-orange.svg)](https://imbeyondidentity.github.io/Split/)

[Русская версия](README_ru.md)

Split a track into **vocals**, **drums**, **bass** and **other**, and
get a ready-made **instrumental** (drums + bass + other) as a fifth
file. Two versions: a browser app (GitHub Pages) and a Python CLI.
Both use Demucs (HTDemucs), and both save MP3 or WAV.

*RU: Делит трек на вокал, ударные, бас и остальное и собирает готовый минус. Две версии — в браузере и в командной строке.*

## Browser

- Drop a track in, pick MP3 (128–320 kbps) or WAV (16/24 bit)
- Five results: vocals, instrumental, drums, bass, other — each with
  a player and a download button, plus one ZIP with everything
- "First 30 s" checks the result quickly before you commit to the
  full track
- Runs fully locally — your audio is never uploaded
- The model (about 172 MB) is downloaded once from Hugging Face and
  then kept in the browser cache
- On GitHub Pages the browser runs the model on one thread, so a full
  track takes a while — use the CLI for long tracks or batches
- A phone may run out of memory on a full track; a computer is safer
- Reads what the browser can decode (MP3, WAV, M4A, FLAC, MP4 and
  so on). For anything else, use the CLI

## CLI

Needs Python 3.9+, [ffmpeg](https://ffmpeg.org/download.html) and
Demucs (which brings PyTorch with it).

```bash
pip install demucs numpy
```

```bash
python split.py song.mp3
python split.py song.mp3 -f wav
python split.py song.mp3 -m htdemucs_ft
python split.py ./songs -r -o ./out
```

The first run downloads the model weights. Results go into a folder
next to the track:

```
song_split/
  song_vocals.mp3
  song_instrumental.mp3
  song_drums.mp3
  song_bass.mp3
  song_other.mp3
```

| Option | |
|---|---|
| `-f mp3\|wav` | output format |
| `-b 128\|192\|256\|320` | MP3 bitrate |
| `--bits 16\|24\|32` | WAV bit depth (32 = float) |
| `-m htdemucs\|htdemucs_ft` | model; `_ft` is cleaner, about 4x slower |
| `--shifts N` | random shifts: cleaner, slower (default 1) |
| `--device auto\|cpu\|cuda\|mps` | where to run (default auto) |
| `--no-instrumental` | skip the instrumental |
| `-o DIR` | output folder |
| `-r` | include subfolders |
| `--overwrite` | replace existing results |


## Credits

- [Demucs](https://github.com/facebookresearch/demucs) by Meta
  (HTDemucs model), MIT
- [demucs-web](https://github.com/timcsy/demucs-web) by timcsy — the
  browser engine here is adapted from it, MIT. See [NOTICE](NOTICE)
- [ONNX Runtime Web](https://onnxruntime.ai/), loaded from a CDN
- [lamejs](https://github.com/zhuker/lamejs) (MP3) and
  [JSZip](https://stuk.github.io/jszip/) (ZIP), loaded from a CDN

Use it on audio you have the right to process.

## Licence

MIT © BeyondiDentity — see [`LICENSE`](LICENSE).
