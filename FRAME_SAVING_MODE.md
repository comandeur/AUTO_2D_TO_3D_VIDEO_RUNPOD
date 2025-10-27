# Frame Saving Mode (Recommended)

This repository now supports **frame-saving mode** as the default processing method. Instead of encoding video directly on RunPod (which can fail with OOM errors), individual PNG frames are saved for download and local encoding.

## Why Frame-Saving Mode?

**Problem with Direct Video Encoding:**
- Video-Depth-Anything loads ALL processed frames into system RAM to encode the final video
- Long videos (7+ minutes, 10,000+ frames) require 16GB+ RAM for encoding
- OOM (Out Of Memory) kills lose all 30+ minutes of processing work
- No way to recover if encoding fails

**Solution - Frame-Saving Mode:**
- ✅ Each depth frame saved immediately after GPU processing
- ✅ RAM usage stays minimal (only 1 frame in RAM at a time)
- ✅ If process fails, all completed frames are already saved
- ✅ Download frames and encode locally with full control
- ✅ Keep frames as backup for re-encoding with different settings
- ✅ No risk of losing processing work

## How It Works

### 1. Configuration (Default: Enabled)

In `config.yaml`:
```yaml
processing:
  # Save individual frames instead of encoding video (RECOMMENDED)
  save_frames_only: true  # Default
```

### 2. Run Processing

```bash
./process_video.py
```

The script will automatically use frame-saving mode.

### 3. Output Structure

```
depth/PregnancyCravingsGoneWrongNew/
├── depth_frames/      # Grayscale depth PNG frames (for 3D conversion)
│   ├── 00000.png
│   ├── 00001.png
│   ├── 00002.png
│   └── ... (all 10,000+ frames)
├── source_frames/     # Original video frames (for reference)
│   ├── 00000.png
│   ├── 00001.png
│   └── ...
└── metadata.txt       # FPS, frame count, settings
```

### 4. Package for Download

```bash
./package_frames.sh
```

This creates a compressed `.tar.gz` archive (typically 2-5GB depending on video).

### 5. Download Options

**A. RunPod Web Interface (Easiest):**
- Go to pod → File Browser
- Navigate to `/workspace/AUTO_2D_TO_3D_VIDEO_RUNPOD/`
- Right-click the `.tar.gz` file → Download

**B. SCP (from your local machine):**
```bash
scp root@YOUR_RUNPOD_IP:~/AUTO_2D_TO_3D_VIDEO_RUNPOD/depth_frames_*.tar.gz .
```

**C. HTTP Server (from RunPod):**
```bash
python3 -m http.server 8000
# Access: http://YOUR_RUNPOD_IP:8000/
```

### 6. Encode Locally

Extract and encode on your local machine:

```bash
# Extract
tar -xzf depth_frames_*.tar.gz
cd PregnancyCravingsGoneWrongNew/depth_frames

# Encode video
ffmpeg -framerate 23.98 -i %05d.png \
  -c:v libx264 -crf 18 -pix_fmt yuv420p \
  -movflags +faststart depth_video.mp4
```

See [ENCODE_LOCALLY.md](ENCODE_LOCALLY.md) for detailed instructions.

## Benefits

### 1. No OOM Failures
- Processing never runs out of RAM
- Each frame saved immediately
- No risk of losing work

### 2. Flexibility
- Encode with different quality settings
- Try multiple CRF values
- Change FPS without re-processing
- Create both high-quality and compressed versions

### 3. Backup
- Keep original frames
- Re-encode anytime
- No need to re-process on GPU

### 4. Cost Savings
- Process once on expensive GPU pod
- Encode multiple times on local machine for free
- Avoid re-processing costs if encoding settings need adjustment

### 5. Reliability
- Download frames at your convenience
- Terminate RunPod instance immediately after processing
- No risk of spot instance termination during encoding

## Comparison: Frame-Saving vs Direct Encoding

| Aspect | Frame-Saving Mode | Direct Encoding Mode |
|--------|-------------------|----------------------|
| **RAM Usage** | Minimal (~1GB) | High (16GB+) |
| **OOM Risk** | None | High on long videos |
| **Work Recovery** | All frames saved | Lost if OOM occurs |
| **Flexibility** | Re-encode anytime | One-shot, fixed settings |
| **Download Size** | 2-5GB compressed | N/A (creates video) |
| **Local Encoding** | Full control | Not possible |
| **Backup** | Yes (keep frames) | No backup |
| **RunPod Cost** | Lower (terminate early) | Higher (wait for encoding) |

## When to Use Direct Encoding Mode

You might want to disable frame-saving mode (`save_frames_only: false`) if:

1. **Short videos only** (< 5 minutes)
2. **High RAM RunPod instance** (32GB+ system RAM)
3. **Don't want to download** large frame archives
4. **Network limitations** prevent large downloads
5. **Just need quick preview** without full quality

For most users processing long videos (7+ minutes), **frame-saving mode is strongly recommended**.

## Technical Details

### Frame Naming Convention
Frames are named with zero-padded 5-digit numbers: `00000.png` to `99999.png`

This allows for videos up to 99,999 frames (~1 hour at 30fps).

### Grayscale Depth Maps
When `grayscale: true` in config (default for 3D conversion):
- Each pixel value (0-255) represents depth
- 0 = furthest, 255 = closest
- Pure grayscale, no color palette
- Compatible with StereoPhotoMaker and other 3D tools

### Colorized Depth Maps
When `grayscale: false`:
- Depth visualized with Inferno colormap
- Blue = far, Yellow/White = close
- For visualization only, not for 3D conversion

### Metadata File
`metadata.txt` contains:
```
input_video: /path/to/video.mp4
total_frames: 10272
fps: 23.98
encoder: vitl
grayscale: true
frame_naming: %05d.png
```

Used for local encoding with correct settings.

## Troubleshooting

### "No frames found" after processing

If you used old code (before frame-saving mode was added), the process tried to encode video directly and failed. You'll need to re-process with the updated code.

### Frames are colorized instead of grayscale

Check `config.yaml`:
```yaml
depth_settings:
  grayscale: true  # Must be true for 3D conversion
```

### Package script can't find frames

Make sure processing completed successfully. Check:
```bash
ls depth/PregnancyCravingsGoneWrongNew/depth_frames/
```

You should see thousands of PNG files.

### Download too slow

The archive is large (2-5GB). Consider:
- Using `rsync` instead of SCP for resume capability
- Using RunPod's network volume for faster access
- Processing shorter video segments

## Next Steps After Encoding

Once you have `depth_video.mp4`, you can create 3D Side-by-Side video:

1. **Use StereoPhotoMaker** (Windows):
   - Load original video as "Left"
   - Load depth video as "Right" (depth map)
   - Stereo → Generate from Depth Map
   - Export as SBS 3D video

2. **Use other 3D tools** that accept depth maps

3. **Use VR video players** with depth support

## Questions?

- Frame-saving technical details: See `run_save_frames.py`
- Encoding parameters: See [ENCODE_LOCALLY.md](ENCODE_LOCALLY.md)
- Troubleshooting: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Hardware requirements: See [HARDWARE_REQUIREMENTS.md](HARDWARE_REQUIREMENTS.md)
