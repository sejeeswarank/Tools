# Architecture Decisions

| ADR ID | Title | Date | Status |
|---|---|---|---|
| ADR-001 | Dynamic FFmpeg Resolution with System and Pip Fallbacks | 2026-10-27 | ACCEPTED |

## ADR-001: Dynamic FFmpeg Resolution with System and Pip Fallbacks
- **Context**: Users running media processing utilities on various machines may not have FFmpeg installed system-wide.
- **Decision**: Use `shutil.which("ffmpeg")` first, and if not present, dynamically import and invoke `imageio_ffmpeg.get_ffmpeg_exe()`.
- **Consequences**: Minimizes setup friction while maintaining full compatibility with system-level optimized FFmpeg builds.
