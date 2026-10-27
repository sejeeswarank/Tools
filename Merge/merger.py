"""
Audio + video merger.

Usage:
    python merger.py video.mp4 audio.mp3 output.mp4
    python merger.py video.mp4 audio.mp3 output.mp4 --shortest

Needs ffmpeg. Either install it system-wide, or just run:
    pip install imageio-ffmpeg
and this script will use the ffmpeg binary that package ships with.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def get_ffmpeg() -> str:
    """Find ffmpeg on PATH, else fall back to the pip-installed binary."""
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        sys.exit(
            "ffmpeg not found. Install it, or run: pip install imageio-ffmpeg"
        )


def merge(video: Path, audio: Path, output: Path, shortest: bool = False) -> None:
    for f in (video, audio):
        if not f.is_file():
            sys.exit(f"File not found: {f}")

    cmd = [
        get_ffmpeg(),
        "-y",                       # overwrite output
        "-i", str(video),
        "-i", str(audio),
        "-map", "0:v:0",            # video stream from first input
        "-map", "1:a:0",            # audio stream from second input
        "-c:v", "copy",             # no video re-encode: fast, lossless
        "-c:a", "aac",              # audio to AAC (safe for mp4)
        "-b:a", "192k",
    ]
    if shortest:
        cmd.append("-shortest")     # cut to the shorter of the two
    cmd.append(str(output))

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(f"ffmpeg failed:\n{result.stderr[-1500:]}")
    print(f"Done: {output}")


def main() -> None:
    p = argparse.ArgumentParser(description="Merge an audio file into a video.")
    p.add_argument("video", type=Path)
    p.add_argument("audio", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--shortest", action="store_true",
                   help="end output when the shorter input ends")
    args = p.parse_args()
    merge(args.video, args.audio, args.output, args.shortest)


if __name__ == "__main__":
    main()