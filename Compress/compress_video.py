"""
Video compressor with live progress (H.265, falls back to H.264).

Modes:
  1) Percent reduction (default, 85%):
        python compress_video.py input.mp4 output.mp4
        python compress_video.py input.mp4 output.mp4 --reduce 80
  2) Exact size, two-pass:
        python compress_video.py input.mp4 output.mp4 --target-gb 2
  3) Constant quality, size depends on the video:
        python compress_video.py input.mp4 output.mp4 --crf 26

Needs ffmpeg. Either install it, or run:  pip install imageio-ffmpeg
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

AUDIO_KBPS = 128


def get_ffmpeg() -> str:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        sys.exit("ffmpeg not found. Install it, or run: pip install imageio-ffmpeg")


def has_encoder(ffmpeg: str, name: str) -> bool:
    r = subprocess.run([ffmpeg, "-hide_banner", "-encoders"], capture_output=True, text=True)
    return name in r.stdout


def probe_duration(ffmpeg: str, path: Path):
    r = subprocess.run([ffmpeg, "-i", str(path)], capture_output=True, text=True)
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", r.stderr)
    if not m:
        return None
    h, mi, s = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(s)


def fmt_time(seconds: float) -> str:
    seconds = int(max(seconds, 0))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:d}:{m:02d}:{s:02d}"


def draw_bar(label: str, done: float, total: float, started: float) -> None:
    pct = min(done / total, 1.0) if total else 0.0
    width = 28
    filled = int(width * pct)
    bar = "#" * filled + "-" * (width - filled)
    elapsed = time.time() - started
    eta = (elapsed / pct - elapsed) if pct > 0.01 else 0
    sys.stdout.write(
        f"\r{label} [{bar}] {pct * 100:5.1f}%  {fmt_time(done)}/{fmt_time(total)}  ETA {fmt_time(eta)}  "
    )
    sys.stdout.flush()


def run(ffmpeg: str, args: list, total: float, label: str, cwd=None) -> None:
    cmd = [ffmpeg, "-y", *args]
    # insert progress flags just before the output path (last arg)
    cmd = cmd[:-1] + ["-progress", "pipe:1", "-nostats", cmd[-1]]
    started = time.time()
    with tempfile.TemporaryFile(mode="w+") as err:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=err, text=True, cwd=cwd)
        for line in proc.stdout:
            key, _, val = line.strip().partition("=")
            if key in ("out_time_us", "out_time_ms"):
                try:
                    done = int(val) / 1_000_000
                except ValueError:
                    continue
                if total:
                    draw_bar(label, done, total, started)
        proc.wait()
        if proc.returncode != 0:
            err.seek(0)
            print()
            sys.exit(f"ffmpeg failed:\n{err.read()[-2000:]}")
    if total:
        draw_bar(label, total, total, started)
    print()


def compress(src: Path, dst: Path, crf, target_gb, reduce, preset: str) -> None:
    if not src.is_file():
        sys.exit(f"File not found: {src}")
    if src.resolve() == dst.resolve():
        sys.exit("Output must be a different file from the input.")

    ffmpeg = get_ffmpeg()
    src, dst = src.resolve(), dst.resolve()

    if has_encoder(ffmpeg, "libx265"):
        codec, extra = "libx265", ["-tag:v", "hvc1"]
        print("Encoder: H.265 (libx265)")
    else:
        codec, extra = "libx264", []
        print("libx265 not available in this ffmpeg build; using H.264 (bigger files).")

    duration = probe_duration(ffmpeg, src) or 0.0
    in_gb = src.stat().st_size / 1e9
    print(f"Input: {in_gb:.2f} GB, duration {fmt_time(duration)}")

    common_out = [
        "-map", "0:v:0", "-map", "0:a?",
        "-c:a", "aac", "-b:a", f"{AUDIO_KBPS}k",
        "-movflags", "+faststart",
    ]

    if reduce is not None:
        target_gb = in_gb * (1 - reduce / 100)
        print(f"Reducing by {reduce:g}% -> aiming for ~{target_gb:.2f} GB")

    if target_gb:
        if not duration:
            sys.exit("Could not read the video duration; target-size mode needs it.")
        total_kbps = target_gb * 1e9 * 8 / duration / 1000
        video_kbps = int((total_kbps - AUDIO_KBPS) * 0.96)  # small safety margin
        if video_kbps < 300:
            sys.exit(f"Target too small for this length ({video_kbps} kbps video). Pick a larger size.")
        print(f"Target {target_gb} GB -> video bitrate ~{video_kbps} kbps")

        with tempfile.TemporaryDirectory() as tmp:
            if codec == "libx265":
                p1 = ["-x265-params", "pass=1:stats=pass.log"]
                p2 = ["-x265-params", "pass=2:stats=pass.log"]
            else:
                p1, p2 = ["-pass", "1", "-passlogfile", "pass"], ["-pass", "2", "-passlogfile", "pass"]
            base = ["-i", str(src), "-c:v", codec, "-b:v", f"{video_kbps}k", "-preset", preset]
            run(ffmpeg, base + p1 + ["-an", "-f", "null", os.devnull], duration, "Pass 1/2", cwd=tmp)
            run(ffmpeg, base + p2 + extra + common_out + [str(dst)], duration, "Pass 2/2", cwd=tmp)
    else:
        args = ["-i", str(src), "-c:v", codec, "-crf", str(crf), "-preset", preset] + extra + common_out + [str(dst)]
        run(ffmpeg, args, duration, "Encoding")

    out_gb = dst.stat().st_size / 1e9
    print(f"Done: {dst}\n{in_gb:.2f} GB -> {out_gb:.2f} GB ({(1 - out_gb / in_gb) * 100:.0f}% smaller)")


def main() -> None:
    p = argparse.ArgumentParser(description="Compress a video with H.265.")
    p.add_argument("input", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--reduce", type=float,
                   help="shrink the file by this percent, e.g. 85 (default when no other mode is given)")
    p.add_argument("--crf", type=int,
                   help="constant-quality mode instead: lower = better/bigger (H.265 range 22-28, try 26)")
    p.add_argument("--target-gb", type=float, help="aim for an exact output size in GB (two-pass)")
    p.add_argument("--preset", default="medium",
                   choices=["ultrafast", "veryfast", "faster", "fast", "medium", "slow", "slower"],
                   help="slower = smaller file for the same quality, but takes longer")
    a = p.parse_args()
    if a.reduce is None and a.crf is None and a.target_gb is None:
        a.reduce = 85
    if a.reduce is not None and not 10 <= a.reduce <= 95:
        sys.exit("--reduce must be between 10 and 95")
    compress(a.input, a.output, a.crf, a.target_gb, a.reduce, a.preset)


if __name__ == "__main__":
    main()
