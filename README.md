# Tools

A collection of lightweight, practical command-line utilities for video processing, compression, and audio/video merging powered by FFmpeg and Python.

---

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Tools Included](#tools-included)
  - [1. Video Compressor (`Compress/`)](#1-video-compressor-compress)
    - [Single Video Compression (`compress_video.py`)](#single-video-compression-compress_videopy)
    - [Batch Video Compression (`batch.py`)](#batch-video-compression-batchpy)
  - [2. Audio & Video Merger (`Merge/`)](#2-audio--video-merger-merge)
    - [Usage (`merger.py`)](#usage-mergerpy)
- [Notes & Quick Reference](#notes--quick-reference)

---

## Overview

This repository contains utility scripts designed to simplify common media processing tasks:
- **`Compress/`**: Efficient video compression utilizing H.265 (HEVC) or H.264, supporting percentage-based reduction, target file size, constant quality (CRF), and NVIDIA GPU-accelerated batch compression (`hevc_nvenc`).
- **`Merge/`**: Fast audio and video multiplexer that combines separate audio and video tracks without re-encoding video.

---

## Prerequisites

Both tools require **FFmpeg**. You can either:
1. Install FFmpeg on your system PATH:
   - **Windows**: `winget install Gyan.FFmpeg` or `choco install ffmpeg`
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg`
2. **OR** install the Python FFmpeg package:
   ```bash
   pip install imageio-ffmpeg
   ```
   The scripts will automatically detect and use the bundled FFmpeg binary.

---

## Tools Included

### 1. Video Compressor (`Compress/`)

#### Single Video Compression (`compress_video.py`)
Compresses video using H.265 (`libx265` with fallback to `libx264`) with real-time CLI progress bar, estimated time remaining, and size reporting.

**Modes:**
1. **Percentage Reduction (Default: 85% reduction):**
   ```bash
   python compress_video.py input.mp4 output.mp4
   # Or specify custom reduction percentage (10 - 95):
   python compress_video.py input.mp4 output.mp4 --reduce 80
   ```

2. **Target File Size (Two-Pass):**
   ```bash
   python compress_video.py input.mp4 output.mp4 --target-gb 2
   ```

3. **Constant Quality (CRF Mode):**
   ```bash
   # Lower CRF = higher quality / larger file (recommended range 22-28, default 26)
   python compress_video.py input.mp4 output.mp4 --crf 26
   ```

**Preset Options:**
You can specify encoding speed vs. compression ratio using `--preset`:
`ultrafast`, `veryfast`, `faster`, `fast`, `medium` (default), `slow`, `slower`.

---

#### Batch Video Compression (`batch.py`)
Hardware-accelerated batch video compression utilizing NVIDIA NVENC (`hevc_nvenc`) with CQ 30 and P6 high-quality preset.

**Instructions:**
- Run inside the folder containing your `.mp4` video files:
  ```bash
  python batch.py
  ```
- Or pass the target directory as an argument:
  ```bash
  python batch.py path/to/videos
  ```

**Behavior:**
- Automatically creates an `out/` directory inside the source folder.
- Skips already processed files.
- Writes names of any failed videos to `failed.txt`.
- Emits progress and compression statistics (original GB -> compressed GB).

---

### 2. Audio & Video Merger (`Merge/`)

#### Usage (`merger.py`)
Merges an audio track into a video file. Copies video stream directly without re-encoding (lossless and extremely fast) while encoding audio to standard AAC 192k for maximum MP4 compatibility.

**Syntax:**
```bash
python merger.py <video_file> <audio_file> <output_file.mp4> [--shortest]
```

**Examples:**
- Basic merge:
  ```bash
  python merger.py input_video.mp4 input_audio.mp3 output.mp4
  ```
- End output when the shorter input track ends:
  ```bash
  python merger.py input_video.mp4 input_audio.wav output.mp4 --shortest
  ```

---

## Notes & Quick Reference

As noted in each module's `Notes.txt`:

- **Batch Compressor:**
  ```bash
  # Run inside the video folder:
  python batch.py
  ```
- **Audio/Video Merger:**
  ```bash
  # Merge command pattern:
  python merger.py <input_video> <input_audio> <output.mp4> --shortest
  ```
