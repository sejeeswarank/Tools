# Project Overview

## Purpose
`Tools` provides automated, accessible command-line utilities for common media engineering tasks. Rather than manually composing complex FFmpeg command strings, users can compress large video files using modern codecs (H.265/NVENC) and cleanly multiplex audio and video streams with simple Python scripts.

## Target Audience
Engineers, creators, and developers needing quick, robust media compression and stream merging with minimal setup.

## Technology Stack
- **Language**: Python 3.8+
- **Core Processing Engine**: FFmpeg (either installed system-wide or via `imageio-ffmpeg`)
- **Acceleration**: NVIDIA NVENC (`hevc_nvenc`) for batch processing, CPU `libx265` / `libx264` for single video compression.
