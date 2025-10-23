# Troubleshooting Guide

Common issues and solutions for the 2D to 3D video conversion workflow.

---

## Installation & Setup Issues

### Error: `ModuleNotFoundError: No module named 'cv2'`

**Problem:** OpenCV (cv2) is not installed.

**Solution:**

```bash
pip3 install opencv-python opencv-python-headless
```

Or install all dependencies manually:
```bash
cd Video-Depth-Anything
pip3 install -r requirements.txt
```

**Why it happens:**
- The Video-Depth-Anything requirements.txt should install opencv-python
- Sometimes the installation fails silently
- May need system dependencies for opencv

**Alternative fix with system packages:**
```bash
apt-get update
apt-get install -y python3-opencv libopencv-dev
pip3 install opencv-python
```

---

### Error: `ModuleNotFoundError: No module named 'torch'`

**Problem:** PyTorch is not installed or not found.

**Solution:**

Make sure you're using a RunPod template with PyTorch pre-installed, or install it manually:

```bash
# For CUDA 12.1
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# For CUDA 11.8
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

**Check your CUDA version:**
```bash
nvidia-smi
```

---

### Error: `ModuleNotFoundError: No module named 'yaml'`

**Problem:** PyYAML is not installed.

**Solution:**
```bash
pip3 install pyyaml
```

---

### Error: `ModuleNotFoundError: No module named 'tqdm'`

**Problem:** tqdm (progress bar library) is not installed.

**Solution:**
```bash
pip3 install tqdm
```

---

### Error: `ModuleNotFoundError: No module named 'einops'`

**Problem:** einops (tensor operations library) is not installed.

**Solution:**
```bash
pip3 install einops
```

---

### Error: `ModuleNotFoundError: No module named 'easydict'`

**Problem:** easydict (dictionary access library) is not installed.

**Solution:**
```bash
pip3 install easydict
```

---

### Error: `ModuleNotFoundError: No module named 'matplotlib'`

**Problem:** matplotlib (plotting and visualization library) is not installed.

**Solution:**
```bash
pip3 install matplotlib
```

---

### Error: `ModuleNotFoundError: No module named 'imageio'`

**Problem:** imageio (image/video I/O library) is not installed.

**Solution:**
```bash
pip3 install imageio imageio-ffmpeg
```

---

### Error: `ModuleNotFoundError: No module named 'xformers'`

**Problem:** xformers (efficient transformer operations library) is not installed.

**Solution:**
```bash
pip3 install xformers
```

**Note:** xformers is important for:
- Memory optimization during processing
- Faster transformer operations
- Better GPU utilization

---

### Quick Fix for All Missing Dependencies

If you're getting multiple `ModuleNotFoundError` messages, run:

```bash
./fix_dependencies.sh
```

This script automatically installs all common missing dependencies.

Or manually install all common dependencies:
```bash
pip3 install opencv-python opencv-python-headless tqdm pyyaml einops easydict matplotlib imageio imageio-ffmpeg xformers notebook ipywidgets
```

---

### Error: `CUDA out of memory`

**Problem:** Your GPU doesn't have enough VRAM for the current settings.

**Solutions:**

1. **Switch to smaller model:**
   ```yaml
   # In config.yaml
   depth_settings:
     encoder: "vits"  # Change from "vitl" to "vits"
   ```

2. **Use FP16 instead of FP32:**
   ```yaml
   depth_settings:
     fp32: false  # Make sure this is false
   ```

3. **Reduce video resolution:**
   - Downscale your input video before processing
   - Use 1080p instead of 4K

4. **Close other GPU processes:**
   ```bash
   # Check what's using GPU
   nvidia-smi

   # Kill other Python processes if needed
   pkill -f python
   ```

5. **Use a pod with more VRAM:**
   - Minimum 8GB for small model
   - 16GB+ for large model recommended
   - 24GB for comfortable 4K processing

---

### Error: `ffmpeg: command not found`

**Problem:** FFmpeg is not installed.

**Solution:**
```bash
apt-get update
apt-get install -y ffmpeg
```

Verify installation:
```bash
ffmpeg -version
```

---

### Error: `git: command not found`

**Problem:** Git is not installed.

**Solution:**
```bash
apt-get update
apt-get install -y git
```

---

## Processing Issues

### Error: No videos found in 'in/' folder

**Problem:** The script can't find video files in the input folder.

**Solutions:**

1. **Check video files are in the correct location:**
   ```bash
   ls -lh in/
   ```

2. **Verify file extensions are supported:**
   - Supported: .mp4, .avi, .mov, .mkv, .webm, .flv
   - Try renaming or converting your video

3. **Check file permissions:**
   ```bash
   chmod 644 in/*.mp4
   ```

---

### Video processing is very slow

**Possible causes and solutions:**

1. **Using Large model on low-end GPU:**
   - Switch to small model: `encoder: "vits"`

2. **Using FP32 precision:**
   - Switch to FP16: `fp32: false`

3. **High resolution video:**
   - Consider downscaling to 1080p
   - 4K videos take 3-4x longer

4. **GPU throttling due to temperature:**
   ```bash
   # Check GPU temperature
   nvidia-smi
   ```
   - Ensure good cooling
   - Reduce load if temperature is high

5. **Using On-Demand instead of GPU-optimized pod:**
   - Choose pods with better GPUs (RTX 4090, A100)

---

### Error: `RuntimeError: CUDA error: device-side assert triggered`

**Problem:** Usually indicates a bug in the model or incompatible CUDA/PyTorch versions.

**Solutions:**

1. **Update PyTorch:**
   ```bash
   pip3 install --upgrade torch torchvision
   ```

2. **Check CUDA compatibility:**
   ```bash
   python3 -c "import torch; print(torch.cuda.is_available())"
   python3 -c "import torch; print(torch.version.cuda)"
   ```

3. **Try FP32 instead of FP16:**
   ```yaml
   depth_settings:
     fp32: true
   ```

---

### Error: `FileNotFoundError: metric_video_depth_anything_vitl.pth`

**Problem:** You have `metric: true` in config.yaml but the metric depth models are not available.

**Quick Solution:**

Edit `config.yaml` and change:
```yaml
depth_settings:
  metric: false  # Change from true to false
```

**Why this happens:**
- Metric depth models give actual distance measurements (meters)
- Relative depth models give depth relationships (closer/farther)
- **Metric models may not be publicly available** on Hugging Face
- **For 3D/SBS conversion, you don't need metric depth** - relative depth works perfectly

**When to use each:**
- **Relative depth (metric: false)**: 3D conversion, SBS video, depth effects ← **Use this**
- **Metric depth (metric: true)**: Actual distance measurements, robotics, AR applications

**If you really need metric depth:**

Try downloading manually:
```bash
cd Video-Depth-Anything/checkpoints

# Try Small metric model
wget https://huggingface.co/depth-anything/Video-Depth-Anything-Small/resolve/main/metric_video_depth_anything_vits.pth

# Try Large metric model
wget https://huggingface.co/depth-anything/Video-Depth-Anything-Large/resolve/main/metric_video_depth_anything_vitl.pth
```

If downloads fail, metric models are not publicly available. Use `metric: false` instead.

---

### Model checkpoint download fails

**Problem:** wget cannot download model checkpoints from Hugging Face.

**Solutions:**

1. **Check internet connection:**
   ```bash
   ping google.com
   ```

2. **Retry the setup:**
   ```bash
   ./setup_runpod.sh
   ```

3. **Manual download:**
   ```bash
   cd Video-Depth-Anything/checkpoints

   # Small model (relative depth)
   wget https://huggingface.co/depth-anything/Video-Depth-Anything-Small/resolve/main/video_depth_anything_vits.pth

   # Large model (relative depth)
   wget https://huggingface.co/depth-anything/Video-Depth-Anything-Large/resolve/main/video_depth_anything_vitl.pth
   ```

4. **Download from browser and upload to RunPod:**
   - Download models from Hugging Face in your browser
   - Upload via RunPod web interface to `Video-Depth-Anything/checkpoints/`

---

## Output Issues

### Depth video is blank or all black

**Possible causes:**

1. **Input video is corrupted or unreadable:**
   - Test with `ffmpeg -i input.mp4` to verify

2. **Wrong color space or encoding:**
   - Try re-encoding input: `ffmpeg -i input.mp4 -c:v libx264 output.mp4`

3. **Model checkpoint is corrupted:**
   - Re-download the model checkpoint
   - Verify file size matches expected size

---

### Depth map looks incorrect or inverted

**Solutions:**

1. **This is normal for some videos:**
   - Depth estimation can struggle with:
     - Very dark scenes
     - Mirrors and reflections
     - Transparent objects
     - Uniform textures (blank walls)

2. **Try metric depth:**
   ```yaml
   depth_settings:
     metric: true
   ```

3. **Use the Large model for better quality:**
   ```yaml
   depth_settings:
     encoder: "vitl"
   ```

---

### Output is colorized instead of grayscale

**Problem:** Config has `grayscale: false`

**Solution:**
```yaml
# In config.yaml
depth_settings:
  grayscale: true  # MUST be true for 3D conversion
```

For 3D/SBS conversion, grayscale is **required**. See [DEPTH_MAP_GUIDE.md](DEPTH_MAP_GUIDE.md) for details.

---

## RunPod-Specific Issues

### Pod keeps terminating (Spot Instance)

**Problem:** Spot instances can be reclaimed by other users.

**Solutions:**

1. **Use On-Demand instance for reliability:**
   - More expensive but guaranteed availability

2. **Use Network Volume for persistent storage:**
   - Saves models and outputs even if pod terminates

3. **Save work frequently:**
   - Download processed videos immediately

---

### Can't upload files to RunPod

**Solutions:**

1. **Use RunPod web file manager:**
   - Access via RunPod dashboard

2. **Use wget to download directly to pod:**
   ```bash
   cd in/
   wget https://your-video-url.com/video.mp4
   ```

3. **Use cloud storage (Dropbox, Google Drive):**
   ```bash
   # Install rclone
   curl https://rclone.org/install.sh | bash
   rclone copy dropbox:videos/ in/
   ```

---

### Pod is slow or unresponsive

**Solutions:**

1. **Check GPU utilization:**
   ```bash
   nvidia-smi
   watch -n 1 nvidia-smi  # Real-time monitoring
   ```

2. **Check system resources:**
   ```bash
   htop
   ```

3. **Restart the pod:**
   - Stop and start from RunPod dashboard

---

## Performance Optimization

### How to make processing faster?

1. **Use smaller model:**
   - `encoder: "vits"` is 2x faster than `vitl`

2. **Use FP16 precision:**
   - `fp32: false` is default and faster

3. **Reduce FPS:**
   ```yaml
   depth_settings:
     target_fps: 15  # Process at lower FPS
   ```

4. **Choose faster GPU:**
   - RTX 4090 > RTX 3090 > RTX 3080

5. **Downscale video first:**
   ```bash
   ffmpeg -i input_4k.mp4 -vf scale=1920:1080 input_1080p.mp4
   ```

---

## Getting Help

If you're still experiencing issues:

1. **Check logs carefully:**
   - Read the full error message
   - Note which step fails

2. **Verify system requirements:**
   - Review [HARDWARE_REQUIREMENTS.md](HARDWARE_REQUIREMENTS.md)

3. **Check Video-Depth-Anything issues:**
   - Visit https://github.com/DepthAnything/Video-Depth-Anything/issues

4. **Test with a small video first:**
   - Use a 5-10 second test clip
   - Verify the workflow works before processing long videos

5. **Check this repository's issues:**
   - Someone may have encountered the same problem

---

## Common Error Messages Quick Reference

| Error | Quick Fix |
|-------|-----------|
| `No module named 'cv2'` | `pip3 install opencv-python` |
| `No module named 'torch'` | Install PyTorch from pytorch.org |
| `No module named 'yaml'` | `pip3 install pyyaml` |
| `No module named 'tqdm'` | `pip3 install tqdm` |
| `No module named 'einops'` | `pip3 install einops` |
| `No module named 'easydict'` | `pip3 install easydict` |
| `No module named 'matplotlib'` | `pip3 install matplotlib` |
| `No module named 'imageio'` | `pip3 install imageio imageio-ffmpeg` |
| `No module named 'xformers'` | `pip3 install xformers` |
| `CUDA out of memory` | Use small model or lower resolution |
| `FileNotFoundError: metric_video_depth_anything` | Set `metric: false` in config.yaml |
| `ffmpeg: command not found` | `apt-get install ffmpeg` |
| `No videos found` | Check files are in `in/` folder |
| Blank depth output | Check input video is valid |
| Colorized instead of grayscale | Set `grayscale: true` in config |
| **All missing modules** | Run `./fix_dependencies.sh` |

---

## Debug Mode

To get more detailed output for debugging:

```bash
# Run with verbose output
python3 -v process_video.py

# Check Python path
which python3
python3 --version

# Verify imports
python3 -c "import cv2; print(cv2.__version__)"
python3 -c "import torch; print(torch.__version__)"
python3 -c "import yaml; print('yaml ok')"

# Test Video-Depth-Anything directly
cd Video-Depth-Anything
python3 run.py --help
```

This should help identify where the issue is occurring.
