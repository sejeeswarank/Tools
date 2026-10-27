# Architecture

## Directory Structure
```
Tools/
├── Compress/
│   ├── batch.py             # NVIDIA NVENC batch processor
│   ├── compress_video.py    # Multi-mode single file compressor with live progress
│   └── Notes.txt            # Quick instruction notes
├── Merge/
│   ├── merger.py            # Stream multiplexer (video copy + AAC audio)
│   └── Notes.txt            # Quick instruction notes
├── README.md                # Project documentation & usage instructions
└── docs/                    # Persistent documentation
```

## Subsystem Architecture
- **FFmpeg Detection**: Scripts employ `shutil.which("ffmpeg")` to inspect system PATH, falling back dynamically to `imageio_ffmpeg.get_ffmpeg_exe()`.
- **Progress Reporting**: `compress_video.py` streams `-progress pipe:1` from FFmpeg stdout to calculate microsecond completion, rendering dynamic ASCII progress bars and ETA estimates.
- **Batch Resiliency**: `batch.py` writes output to a staging `.part.mp4` file and atomically renames it upon successful encoding, writing failures to `failed.txt`.
