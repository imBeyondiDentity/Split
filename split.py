#!/usr/bin/env python3
"""
Split — separate a track into vocals, drums, bass and other with
Demucs, and build an instrumental (drums + bass + other).
Writes MP3 or WAV.

Examples:
  python split.py song.mp3
  python split.py song.mp3 -f wav --bits 24
  python split.py song.mp3 -m htdemucs_ft
  python split.py ./songs -r -o ./out
"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Demucs 4.0.1 stores a full model class in its checkpoints, and PyTorch
# 2.6+ refuses to unpickle that by default. The weights come from Meta's
# official release that Demucs downloads itself, so allow the old
# behaviour. This must be set before torch is imported.
os.environ.setdefault("TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD", "1")

AUDIO_EXT = {
    ".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg", ".opus", ".wma",
    ".mp4", ".m4v", ".mov", ".mkv", ".webm", ".avi", ".3gp",
}
WAV_CODEC = {16: "pcm_s16le", 24: "pcm_s24le", 32: "pcm_f32le"}
RATE = 44100
CHANNELS = 2
MODELS = ["htdemucs", "htdemucs_ft"]
STEMS = ["vocals", "instrumental", "drums", "bass", "other"]


def find_ffmpeg():
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg  # optional: pip install imageio-ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


def collect(inputs, recursive):
    files = []
    for raw in inputs:
        p = Path(raw).expanduser()
        if p.is_dir():
            it = p.rglob("*") if recursive else p.glob("*")
            files += sorted(f for f in it
                            if f.is_file()
                            and f.suffix.lower() in AUDIO_EXT)
        elif p.is_file():
            files.append(p)
        else:
            print(f"  ! not found: {raw}", file=sys.stderr)
    return files


def read_audio(ff, src):
    """Decode any file to float32 stereo at 44.1 kHz: array [2, n]."""
    import numpy as np
    cmd = [ff, "-hide_banner", "-loglevel", "error", "-i", str(src),
           "-vn", "-f", "f32le", "-ac", str(CHANNELS),
           "-ar", str(RATE), "pipe:1"]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0 or not r.stdout:
        msg = r.stderr.decode(errors="replace").strip().splitlines()
        raise RuntimeError(msg[-1] if msg else "no audio found")
    data = np.frombuffer(r.stdout, dtype="<f4")
    data = data[: len(data) // CHANNELS * CHANNELS]
    return data.reshape(-1, CHANNELS).T.copy()


def pick_device(name):
    import torch
    if name != "auto":
        return name
    return "cuda" if torch.cuda.is_available() else "cpu"


def load_model(name):
    from demucs.pretrained import get_model
    model = get_model(name)
    model.cpu()
    model.eval()
    return model


def separate_audio(model, wav, shifts, device):
    """wav: float32 [2, n]. Returns {stem: float32 [2, n]}."""
    import numpy as np
    import torch
    from demucs.apply import apply_model

    x = torch.from_numpy(wav)
    ref = x.mean(0)
    mean, std = ref.mean(), ref.std()
    if float(std) < 1e-8:
        raise RuntimeError("the track is silent")
    x = (x - mean) / std
    with torch.no_grad():
        out = apply_model(model, x[None], device=device, shifts=shifts,
                          split=True, overlap=0.25, progress=True)[0]
    out = out * std + mean
    return {name: np.ascontiguousarray(out[i].cpu().numpy(),
                                       dtype=np.float32)
            for i, name in enumerate(model.sources)}


def safe_peak(a, ceiling=0.999):
    peak = float(abs(a).max()) if a.size else 0.0
    return a * (ceiling / peak) if peak > ceiling else a


def write_audio(ff, a, dst, a_args):
    """a: float32 [2, n]; encodes through ffmpeg."""
    raw = a.T.astype("<f4").tobytes()
    cmd = [ff, "-hide_banner", "-loglevel", "error", "-y",
           "-f", "f32le", "-ar", str(RATE), "-ac", str(CHANNELS),
           "-i", "pipe:0"]
    if a_args.format == "mp3":
        cmd += ["-c:a", "libmp3lame", "-b:a", f"{a_args.bitrate}k"]
    else:
        cmd += ["-c:a", WAV_CODEC[a_args.bits]]
    cmd.append(str(dst))
    r = subprocess.run(cmd, input=raw, capture_output=True)
    if r.returncode != 0:
        lines = r.stderr.decode(errors="replace").strip().splitlines()
        raise RuntimeError(lines[-1] if lines else "ffmpeg failed")


def build_stems(stems, with_instrumental=True):
    """Adds the instrumental (drums + bass + other) to the dict."""
    out = dict(stems)
    if with_instrumental:
        out["instrumental"] = (stems["drums"] + stems["bass"]
                               + stems["other"])
    return out


def process(ff, src, folder, a, separate):
    wav = read_audio(ff, src)
    stems = build_stems(separate(wav), not a.no_instrumental)
    folder.mkdir(parents=True, exist_ok=True)
    written = []
    for name in STEMS:
        if name not in stems:
            continue
        dst = folder / f"{src.stem}_{name}.{a.format}"
        write_audio(ff, safe_peak(stems[name]), dst, a)
        written.append(dst)
    return written


def human(n):
    return f"{n / 1048576:.1f} MB" if n > 1048576 else f"{n // 1024} KB"


def main():
    ap = argparse.ArgumentParser(
        prog="split",
        description="Split a track into vocals, drums, bass, other "
                    "and an instrumental.")
    ap.add_argument("inputs", nargs="+",
                    help="audio/video files and/or folders")
    ap.add_argument("-f", "--format", choices=["mp3", "wav"],
                    default="mp3", help="output format (default: mp3)")
    ap.add_argument("-b", "--bitrate", type=int, default=320,
                    choices=[128, 192, 256, 320],
                    help="MP3 bitrate in kbps (default: 320)")
    ap.add_argument("--bits", type=int, default=16, choices=[16, 24, 32],
                    help="WAV bit depth; 32 = float (default: 16)")
    ap.add_argument("-m", "--model", choices=MODELS, default="htdemucs",
                    help="htdemucs is fast; htdemucs_ft is a little "
                         "cleaner and about 4x slower")
    ap.add_argument("--shifts", type=int, default=1,
                    help="random shifts: more is cleaner and slower "
                         "(default: 1)")
    ap.add_argument("--device", default="auto",
                    help="auto, cpu, cuda or mps (default: auto)")
    ap.add_argument("--no-instrumental", action="store_true",
                    help="skip the instrumental file")
    ap.add_argument("-o", "--out", type=Path,
                    help="output folder (default: next to each track)")
    ap.add_argument("-r", "--recursive", action="store_true",
                    help="search subfolders")
    ap.add_argument("--overwrite", action="store_true",
                    help="replace existing results")
    a = ap.parse_args()

    if a.shifts < 0:
        ap.error("--shifts must be zero or more")

    ff = find_ffmpeg()
    if not ff:
        sys.exit("ffmpeg not found. Install it (brew/apt/winget install "
                 "ffmpeg) or run: pip install imageio-ffmpeg")

    files = collect(a.inputs, a.recursive)
    if not files:
        sys.exit("No audio files found.")

    try:
        import numpy  # noqa: F401
        import torch  # noqa: F401
        import demucs  # noqa: F401
    except ImportError as e:
        sys.exit(f"Missing package: {e.name}. Install with:\n"
                 "  pip install demucs numpy")

    device = pick_device(a.device)
    print(f"Model {a.model} on {device}. The first run downloads the "
          "weights.")
    model = load_model(a.model)

    def separate(wav):
        return separate_audio(model, wav, a.shifts, device)

    ok = skipped = failed = 0
    for i, src in enumerate(files, 1):
        base = a.out or src.parent
        folder = base / f"{src.stem}_split"
        tag = f"[{i}/{len(files)}]"
        if folder.exists() and not a.overwrite:
            print(f"{tag} skip  {folder.name} (exists, use --overwrite)")
            skipped += 1
            continue
        print(f"{tag} {src.name}", flush=True)
        try:
            done = process(ff, src, folder, a, separate)
        except Exception as e:  # keep going with the other files
            print(f"{tag} ✗ {e}")
            failed += 1
            continue
        size = sum(p.stat().st_size for p in done)
        print(f"{tag} ✓ {len(done)} files in {folder} ({human(size)})")
        ok += 1

    print(f"\nDone: {ok} ok, {skipped} skipped, {failed} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
