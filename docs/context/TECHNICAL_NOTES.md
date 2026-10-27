# Technical Notes

## NVENC vs Software Encoding
- `Compress/batch.py` leverages `hevc_nvenc` for high-throughput encoding on systems with compatible NVIDIA GPUs.
- `Compress/compress_video.py` detects available encoders at runtime via `ffmpeg -hide_banner -encoders`. If `libx265` is present, it adds `-tag:v hvc1` for Apple/QuickTime compatibility; otherwise, it falls back to `libx264`.

## Progress Tracking
- FFmpeg's `-progress pipe:1` outputs key-value pairs per frame/interval. Reading `out_time_us` or `out_time_ms` allows accurate percentage calculation against total video duration probed from container metadata.
