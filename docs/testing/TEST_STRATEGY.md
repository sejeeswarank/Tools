# Test Strategy

## Verification Methodology
1. **Syntax & CLI Argument Parsing**: Execute Python scripts with `--help` to verify entry points, argument parser definitions, and help texts without side effects.
2. **FFmpeg Detection**: Check detection logic by ensuring `get_ffmpeg()` resolves either via system PATH or `imageio-ffmpeg`.
3. **Git Integration**: Verify remote tracking, clean commits, and branch synchronization with `origin/main`.
