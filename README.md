# 2D to 3D Video Conversion on RunPod

Automated workflow for converting 2D videos to depth maps using GPU acceleration on RunPod, with future support for Side-by-Side (SBS) 3D video output.

## Overview

This project automates the conversion of 2D videos to 3D depth maps using [Video-Depth-Anything](https://github.com/DepthAnything/Video-Depth-Anything), optimized for running on RunPod's high-performance GPU instances.

### Features

- Automated setup script for RunPod instances
- Batch processing of multiple videos
- Real-time progress monitoring (frames/time)
- Configurable depth estimation parameters
- Support for both small and large models
- Preparation for SBS output using StereoPhotoMaker

## Hardware Requirements

**IMPORTANT**: Before starting, please review the [Hardware Requirements Guide](HARDWARE_REQUIREMENTS.md) for:

- **GPU Recommendations**: Which GPU to choose (RTX 4090 recommended)
- **PyTorch Version**: PyTorch 2.0+ with CUDA 11.8 or 12.1
- **Storage Size**: 100GB recommended (30GB minimum)
- **Cost Estimates**: ~$0.50/hour for RTX 4090 spot instance
- **Performance Estimates**: Processing time by video length and resolution

**Quick Answer**: Use **RTX 4090 (24GB)** with **100GB storage** and **PyTorch 2.1 template** for best results.

## Quick Start

### On RunPod

1. **Start a RunPod Instance**
   - Choose a pod with a powerful GPU (RTX 4090, A100, etc.)
   - Use a PyTorch or CUDA-enabled template
   - Recommended: At least 16GB VRAM for large model

2. **Clone This Repository**
   ```bash
   git clone https://github.com/comandeur/AUTO_2D_TO_3D_VIDEO_RUNPOD
   cd AUTO_2D_TO_3D_VIDEO_RUNPOD
   ```

3. **Run Setup Script**
   ```bash
   chmod +x setup_runpod.sh
   ./setup_runpod.sh
   ```

   This will:
   - Install system dependencies (ffmpeg, git, etc.)
   - Clone Video-Depth-Anything repository
   - Download model checkpoints (Small and Large)
   - Install Python dependencies
   - Create necessary folder structure

4. **Add Your Videos**
   ```bash
   # Upload your 2D videos to the 'in' folder
   # You can use RunPod's file upload or wget/curl
   ```

5. **Configure Settings (Optional)**
   Edit `config.yaml` to adjust processing parameters:
   ```bash
   nano config.yaml
   ```

6. **Process Videos**
   ```bash
   ./process_video.py
   ```

## Folder Structure

```
AUTO_2D_TO_3D_VIDEO_RUNPOD/
├── in/                      # INPUT: Place your 2D videos here
├── depth/                   # OUTPUT: Depth videos saved here
├── stereophotomaker/        # For StereoPhotoMaker (future)
├── Video-Depth-Anything/    # Depth estimation tool (auto-cloned)
├── config.yaml              # Configuration file
├── process_video.py         # Main processing script
├── setup_runpod.sh          # Setup script
└── README.md                # This file
```

## Configuration

Edit `config.yaml` to customize processing:

### Depth Settings

- **encoder**: Choose model size
  - `vits`: Small model (28.4M params, faster)
  - `vitl`: Large model (381.8M params, better quality)

- **metric**: Use metric depth estimation (true/false)

- **max_len**: Maximum video length to process (-1 for unlimited)

- **target_fps**: Target FPS for processing (-1 for original)

- **fp32**: Use 32-bit precision instead of 16-bit (slower but more accurate)

- **grayscale**: Output grayscale depth maps without color

### Processing Settings

- **batch_process**: Process all videos in 'in' folder (true) or single file (false)

- **progress_update_frequency**: Show progress every N frames

## Usage Examples

### Basic Usage

Process all videos in the 'in' folder with default settings:

```bash
./process_video.py
```

### Process Single Video

1. Set in `config.yaml`:
   ```yaml
   processing:
     batch_process: false
     single_video_file: "myvideo.mp4"
   ```

2. Run:
   ```bash
   ./process_video.py
   ```

### Use Small Model for Faster Processing

In `config.yaml`:
```yaml
depth_settings:
  encoder: "vits"
```

### High Quality Processing

In `config.yaml`:
```yaml
depth_settings:
  encoder: "vitl"
  fp32: true
```

## Output

Processed videos are saved in the `depth/` folder:

```
depth/
└── video_name/
    ├── depth_video.mp4      # Depth map video
    └── [other outputs]
```

## Progress Monitoring

During processing, you'll see:

- Video information (duration, FPS, resolution, total frames)
- Real-time progress updates
- Frame count and percentage
- Elapsed time and ETA
- Processing speed

Example output:
```
[PROGRESS] Frames: 100/1000 (10.0%) | Elapsed: 0:00:30 | ETA: 0:04:30
```

## Performance Tips

1. **GPU Selection**: Use RTX 4090 or A100 for best performance
2. **Model Selection**: Use `vits` (small) for 2x faster processing
3. **FP16 vs FP32**: Keep fp32=false for 2x speed (minimal quality loss)
4. **Batch Size**: Process multiple videos sequentially for efficiency

## Troubleshooting

### Out of Memory Error

- Switch to smaller model (`encoder: vits`)
- Reduce video resolution before processing
- Use a pod with more VRAM

### Slow Processing

- Use smaller model
- Reduce target_fps
- Ensure fp32 is false

### No Videos Found

- Check videos are in the `in/` folder
- Verify supported formats: .mp4, .avi, .mov, .mkv, .webm, .flv

### Model Download Fails

- Check internet connection
- Manually download from Hugging Face:
  - [Small Model](https://huggingface.co/depth-anything/Video-Depth-Anything-Small)
  - [Large Model](https://huggingface.co/depth-anything/Video-Depth-Anything-Large)
- Place in `Video-Depth-Anything/checkpoints/`

## Future: SBS Conversion

StereoPhotoMaker integration for Side-by-Side 3D output is planned.

### Preparation

1. Download StereoPhotoMaker
2. Place in `stereophotomaker/` folder
3. Future scripts will automate SBS generation from depth maps

## Technical Details

### Video-Depth-Anything

- Based on Depth Anything V2
- Handles arbitrarily long videos
- Maintains consistency across frames
- Two model sizes available

### System Requirements

- CUDA-capable GPU (8GB+ VRAM recommended)
- FFmpeg for video processing
- Python 3.8+
- PyTorch with CUDA support

### Supported Video Formats

- MP4 (recommended)
- AVI
- MOV
- MKV
- WebM
- FLV

## License

- Video-Depth-Anything-Small: Apache-2.0
- Video-Depth-Anything-Large: CC-BY-NC-4.0

Please refer to the original [Video-Depth-Anything repository](https://github.com/DepthAnything/Video-Depth-Anything) for detailed license information.

## Credits

- [Video-Depth-Anything](https://github.com/DepthAnything/Video-Depth-Anything) by DepthAnything team
- [Depth Anything V2](https://github.com/DepthAnything/Depth-Anything-V2)

## Support

For issues specific to this automation:
- Open an issue in this repository

For Video-Depth-Anything issues:
- Visit the [official repository](https://github.com/DepthAnything/Video-Depth-Anything)
