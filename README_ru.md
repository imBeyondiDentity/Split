# Split

[![Licence: MIT](https://img.shields.io/badge/Licence-MIT-yellow.svg)](LICENSE)
[![Open Split](https://img.shields.io/badge/Open-Split-orange.svg)](https://imbeyondidentity.github.io/Split/)

[English version](README.md)

Делит трек на **вокал**, **ударные**, **бас** и **остальное** и
собирает готовый **минус** (ударные + бас + остальное) пятым файлом.
Две версии: в браузере (GitHub Pages) и в командной строке. Обе
работают на Demucs (HTDemucs) и сохраняют MP3 или WAV.

## Браузер

- Перетащи трек, выбери MP3 (128–320 kbps) или WAV (16/24 bit)
- Пять результатов: вокал, минус, ударные, бас, остальное — у каждого
  свой плеер и кнопка «Скачать», плюс один ZIP со всем сразу
- «Первые 30 с» — быстрая проверка результата, прежде чем гнать весь
  трек
- Всё считается локально — звук никуда не загружается
- Модель (около 172 MB) скачивается один раз с Hugging Face и потом
  лежит в кэше браузера
- На GitHub Pages браузер гоняет модель в один поток, поэтому целый
  трек обрабатывается долго — для длинных треков и пачек бери
  Python-версию
- Вкладка телефона не вмещает модель, и Safari её закрывает — на
  телефоне бери ноутбук Colab ниже
- Читает то, что умеет декодировать браузер (MP3, WAV, M4A, FLAC, MP4
  и так далее). Для остального — командная строка

## На телефоне (Colab)

Открой ноутбук, нажми ▶ на шаге 1, потом на шаге 2, выбери трек и
дождись ZIP со всеми пятью файлами. Он запускает `split.py` из этого
репозитория на бесплатном GPU от Google, поэтому на телефон ничего
не ставится.

[Открыть `split.ipynb` в Colab](https://colab.research.google.com/github/imBeyondiDentity/Split/blob/main/split.ipynb)

## Командная строка

Нужны Python 3.9+, [ffmpeg](https://ffmpeg.org/download.html) и Demucs
(он тянет за собой PyTorch).

```bash
pip install demucs numpy
```

```bash
python split.py song.mp3
python split.py song.mp3 -f wav
python split.py song.mp3 -m htdemucs_ft
python split.py ./songs -r -o ./out
```

При первом запуске скачиваются веса модели. Результат ложится в папку
рядом с треком:

```
song_split/
  song_vocals.mp3
  song_instrumental.mp3
  song_drums.mp3
  song_bass.mp3
  song_other.mp3
```

| Опция | |
|---|---|
| `-f mp3\|wav` | формат |
| `-b 128\|192\|256\|320` | битрейт MP3 |
| `--bits 16\|24\|32` | разрядность WAV (32 = float) |
| `-m htdemucs\|htdemucs_ft` | модель; `_ft` чище, примерно в 4 раза медленнее |
| `--shifts N` | случайные сдвиги: чище, медленнее (по умолчанию 1) |
| `--device auto\|cpu\|cuda\|mps` | где считать (по умолчанию auto) |
| `--no-instrumental` | не делать минус |
| `-o DIR` | папка для результата |
| `-r` | искать и в подпапках |
| `--overwrite` | заменять готовые результаты |

## Публикация на GitHub Pages

1. Создай публичный репозиторий `Split`, залей файлы в корень
   (ноутбук Colab читает `split.py` оттуда)
2. Settings → Pages → Source: Deploy from a branch
3. Branch: `main`, папка `/ (root)`
4. Через минуту приложение откроется по адресу
   `https://<username>.github.io/Split/`

## Благодарности

- [Demucs](https://github.com/facebookresearch/demucs) от Meta (модель
  HTDemucs), MIT
- [demucs-web](https://github.com/timcsy/demucs-web) от timcsy — на нём
  основан браузерный движок, MIT. См. [NOTICE](NOTICE)
- [ONNX Runtime Web](https://onnxruntime.ai/), подгружается с CDN
- [lamejs](https://github.com/zhuker/lamejs) (MP3) и
  [JSZip](https://stuk.github.io/jszip/) (ZIP), подгружаются с CDN

Используй на звуке, который имеешь право обрабатывать.

## Лицензия

MIT © BeyondiDentity — см. [`LICENSE`](LICENSE).
