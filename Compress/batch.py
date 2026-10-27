import sys
from pathlib import Path
from compress_video import get_ffmpeg, probe_duration, run

src = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
dst = src / "out"
dst.mkdir(exist_ok=True)
ff = get_ffmpeg()
files = sorted(src.glob("*.mp4"))

for i, f in enumerate(files, 1):
    out = dst / f.name
    if out.exists():
        continue
    tmp = dst / (f.stem + ".part.mp4")
    dur = probe_duration(ff, f) or 0.0
    args = ["-i", str(f),
            "-c:v", "hevc_nvenc", "-cq", "30", "-preset", "p6", "-tune", "hq",
            "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart", str(tmp)]
    try:
        run(ff, args, dur, f"[{i}/{len(files)}]")
        tmp.replace(out)
        print(f"{f.name}: {f.stat().st_size/1e9:.2f} GB -> {out.stat().st_size/1e9:.2f} GB")
    except SystemExit as e:
        print(e)
        tmp.unlink(missing_ok=True)
        with open("failed.txt", "a") as log:
            log.write(f.name + "\n")