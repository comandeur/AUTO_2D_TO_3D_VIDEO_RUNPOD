# Quick Start Guide - RunPod 2D to 3D Video Conversion

## Step-by-Step Instructions for RunPod

### 1. Start Your RunPod Pod

1. Go to [RunPod.io](https://runpod.io)
2. Select a GPU pod:
   - **Recommended**: RTX 4090 or A100
   - **Minimum**: RTX 3090 (16GB VRAM)
3. Choose a template with PyTorch/CUDA
4. Start the pod

### 2. Connect to Your Pod

```bash
# Use the SSH or Web terminal provided by RunPod
```

### 3. Clone and Setup

```bash
# Clone this repository
git clone <your-repo-url>
cd AUTO_2D_TO_3D_VIDEO_RUNPOD

# Run the setup script (this will take 5-10 minutes)
./setup_runpod.sh
```

The setup script will:
- Install system dependencies
- Clone Video-Depth-Anything
- Download AI models (~2-3GB)
- Install Python packages
- Create folder structure

### 4. Upload Your Videos

**Option A: Using RunPod Web UI**
1. Use RunPod's file browser
2. Navigate to `AUTO_2D_TO_3D_VIDEO_RUNPOD/in/`
3. Upload your video files

**Option B: Using wget/curl**
```bash
cd in/
wget https://your-video-url.com/video.mp4
```

**Option C: Using rsync/scp**
```bash
# From your local machine
scp your-video.mp4 user@runpod-ip:/workspace/AUTO_2D_TO_3D_VIDEO_RUNPOD/in/
```

### 5. Configure (Optional)

Edit the configuration file if needed:
```bash
nano config.yaml
```

Key settings:
- `encoder: "vitl"` - Large model (better quality, slower)
- `encoder: "vits"` - Small model (faster, good quality)
- `metric: true` - Use metric depth estimation

### 6. Run the Conversion

```bash
./process_video.py
```

You'll see:
```
================================================================================
2D to 3D Video Conversion - Depth Estimation
================================================================================
Found 1 video(s) to process:
  - myvideo.mp4

================================================================================
Processing: myvideo.mp4
================================================================================
Video info:
  Duration: 30.00s
  FPS: 30.00
  Total frames: 900
  Resolution: 1920x1080

[PROGRESS] Frames: 100/900 (11.1%) | Elapsed: 0:01:30 | ETA: 0:12:00
```

### 7. Download Your Results

Results are saved in the `depth/` folder:

```
depth/
└── myvideo/
    ├── depth_video.mp4
    └── [other files]
```

**Download using RunPod Web UI:**
1. Navigate to `depth/` folder
2. Download the depth video

**Download using scp:**
```bash
# From your local machine
scp -r user@runpod-ip:/workspace/AUTO_2D_TO_3D_VIDEO_RUNPOD/depth ./
```

## Processing Times (Approximate)

| Video Length | Resolution | Model | GPU    | Estimated Time |
|-------------|-----------|-------|--------|----------------|
| 30 seconds  | 1080p     | Small | 4090   | ~2-3 minutes   |
| 30 seconds  | 1080p     | Large | 4090   | ~4-5 minutes   |
| 2 minutes   | 1080p     | Small | 4090   | ~8-10 minutes  |
| 2 minutes   | 1080p     | Large | 4090   | ~15-20 minutes |
| 30 seconds  | 4K        | Small | 4090   | ~5-7 minutes   |
| 30 seconds  | 4K        | Large | 4090   | ~10-15 minutes |

## Tips for RunPod

### Save Costs
- Use **Spot Instances** for cheaper rates
- Process multiple videos in batch
- Stop the pod when not in use

### Optimize Speed
- Use `encoder: "vits"` for 2x faster processing
- Keep `fp32: false` in config
- Use 1080p videos instead of 4K if acceptable

### Persistent Storage
- Use RunPod's **Network Volumes** to keep:
  - Model checkpoints (avoid re-downloading)
  - Processed videos
  - Input videos

### Multiple Videos
Place all videos in the `in/` folder and they'll be processed sequentially:

```bash
in/
├── video1.mp4
├── video2.mp4
└── video3.mp4
```

Run once:
```bash
./process_video.py
```

All videos will be processed automatically!

## Troubleshooting

### "CUDA out of memory"
1. Switch to small model: `encoder: "vits"` in config.yaml
2. Or use a pod with more VRAM

### "No module named 'yaml'"
```bash
pip3 install pyyaml
```

### "ffmpeg: command not found"
```bash
apt-get update && apt-get install -y ffmpeg
```

### Slow Download of Models
- Models are 2-3GB total
- First setup will take longer
- Use Network Volume to avoid re-downloading

## Next Steps

After generating depth maps, you can:
1. Use them for 3D visualization
2. Create anaglyph 3D images
3. Generate Side-by-Side (SBS) stereo video (coming soon with StereoPhotoMaker integration)

## Support

For RunPod-specific issues:
- Check [RunPod Documentation](https://docs.runpod.io)

For this automation:
- Open an issue in this repository

For Video-Depth-Anything:
- Visit [official repo](https://github.com/DepthAnything/Video-Depth-Anything)
