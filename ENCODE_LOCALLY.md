# Encoding Depth Frames Locally

If you downloaded the processed depth frames from RunPod, here's how to encode them into a video on your local machine.

## Prerequisites

Make sure you have FFmpeg installed:

**Windows:**
- Download from https://ffmpeg.org/download.html
- Or use: `winget install FFmpeg` / `choco install ffmpeg`

**Mac:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg  # Ubuntu/Debian
sudo yum install ffmpeg      # CentOS/RHEL
```

## Steps

### 1. Extract the Archive

```bash
tar -xzf depth_frames_PregnancyCravingsGoneWrongNew_*.tar.gz
```

This will create a folder: `PregnancyCravingsGoneWrongNew/` with subdirectories:
- `depth_frames/` - Grayscale depth maps
- `source_frames/` - Original video frames
- `metadata.txt` - Video information

### 2. Verify Frames

```bash
cd PregnancyCravingsGoneWrongNew/depth_frames
ls *.png | head -10  # Check first 10 frames

# Count total frames
ls *.png | wc -l
```

You should see files like: `00000.png`, `00001.png`, `00002.png`, etc.

### 3. Encode Video

**Standard Quality (recommended):**
```bash
ffmpeg -framerate 23.98 -pattern_type glob -i '*.png' \
  -c:v libx264 -crf 18 -pix_fmt yuv420p \
  -movflags +faststart depth_video.mp4
```

**High Quality (larger file):**
```bash
ffmpeg -framerate 23.98 -pattern_type glob -i '*.png' \
  -c:v libx264 -crf 15 -preset slow -pix_fmt yuv420p \
  -movflags +faststart depth_video_hq.mp4
```

**Smaller File Size:**
```bash
ffmpeg -framerate 23.98 -pattern_type glob -i '*.png' \
  -c:v libx264 -crf 23 -preset fast -pix_fmt yuv420p \
  -movflags +faststart depth_video_compressed.mp4
```

### 4. Verify Output

```bash
ffprobe depth_video.mp4
# Or play it
ffplay depth_video.mp4  # Linux/Mac
# Or open in VLC/media player
```

## Encoding Parameters Explained

- **`-framerate 23.98`** - Matches your original video FPS
- **`-pattern_type glob -i '*.png'`** - Input all PNG files in order
- **`-c:v libx264`** - H.264 codec (universal compatibility)
- **`-crf 18`** - Quality (0-51, lower=better, 18=high quality)
- **`-pix_fmt yuv420p`** - Color format for compatibility
- **`-movflags +faststart`** - Optimize for streaming/web playback

## Adjusting Frame Rate

If you need different FPS:

```bash
# 30 FPS
ffmpeg -framerate 30 -pattern_type glob -i '*.png' ...

# 24 FPS
ffmpeg -framerate 24 -pattern_type glob -i '*.png' ...

# 60 FPS (interpolated)
ffmpeg -framerate 60 -pattern_type glob -i '*.png' ...
```

## Alternative: Frame Naming Patterns

If frames have different naming:

```bash
# For frame_00000.png, frame_00001.png, etc.
ffmpeg -framerate 23.98 -i frame_%05d.png ...

# For 00000.png, 00001.png, etc.
ffmpeg -framerate 23.98 -i %05d.png ...
```

## Troubleshooting

### Error: "No such file or directory"

Make sure you're in the directory with the PNG files:
```bash
pwd  # Check current directory
ls *.png | head  # Verify PNG files exist
```

### Error: "Invalid data found"

Check frame integrity:
```bash
file *.png | grep -v "PNG image"  # Find corrupted frames
```

### Video plays too fast/slow

Adjust the `-framerate` parameter to match your original video.

### File size too large

- Increase CRF value (e.g., `-crf 23` or `-crf 28`)
- Use faster preset (e.g., `-preset fast` or `-preset veryfast`)

## Next Steps: Creating 3D SBS Video

Once you have the depth video, you can use StereoPhotoMaker (Windows) to create Side-by-Side 3D:

1. Open StereoPhotoMaker
2. File → Open Left/Right Images
3. Load your original video as "Left"
4. Load the depth video as "Right" (depth map)
5. Stereo → Depth Map → Generate Stereo from Depth Map
6. Adjust depth settings
7. File → Save Stereo Image/Video

Or use other 3D conversion tools that accept depth maps.

## Estimated Encoding Times

Frame count ~10,000 (7 minutes video):
- Fast preset: ~1-2 minutes
- Medium preset: ~3-5 minutes
- Slow preset: ~10-15 minutes

Actual time depends on your CPU speed and frame resolution.

## Questions?

See TROUBLESHOOTING.md for more help or check FFmpeg documentation:
https://ffmpeg.org/documentation.html
