# Metric vs Relative Depth: Which Should You Use?

## Quick Answer

**For 2D to 3D video conversion → Use Relative Depth (`metric: false`)**

This is already set as the default in `config.yaml`.

---

## What's the Difference?

### Relative Depth (metric: false) ← **RECOMMENDED**

**What it is:**
- Compares depth between objects in the scene
- Tells you which objects are closer/farther from each other
- Depth values are normalized (0.0 to 1.0 or 0-255)
- **No absolute distance measurements**

**Example output:**
- Person in foreground: depth value = 200 (bright/close)
- Tree in middle ground: depth value = 127 (medium)
- Mountain in background: depth value = 50 (dark/far)

**Use for:**
- ✅ **3D/SBS video conversion** (StereoPhotoMaker)
- ✅ **Depth-based effects** (bokeh, refocusing)
- ✅ **3D visualization**
- ✅ **Artistic depth maps**
- ✅ **Most consumer applications**

**Advantages:**
- Works on any scene (indoor/outdoor)
- More robust and reliable
- Better quality depth maps
- Models always available
- Faster processing

**Configuration:**
```yaml
depth_settings:
  metric: false
```

---

### Metric Depth (metric: true)

**What it is:**
- Actual distance measurements in meters
- Tells you the real-world distance from camera to object
- Depth values represent actual distances
- **Absolute measurements**

**Example output:**
- Person: 2.5 meters from camera
- Tree: 15.0 meters from camera
- Mountain: 500 meters from camera

**Use for:**
- 📏 Robotics and navigation
- 📏 Augmented Reality (AR)
- 📏 Scientific measurements
- 📏 Applications needing actual distances
- 📏 Scene reconstruction with scale

**Disadvantages for video:**
- ⚠️ Metric models **may not be available** publicly
- ⚠️ Trained on specific datasets (VKITTI, IRS)
- ⚠️ Less robust on varied scenes
- ⚠️ **Not needed for 3D conversion**

**Configuration:**
```yaml
depth_settings:
  metric: true
```

---

## For Your Use Case: 2D to 3D Conversion

### Why Relative Depth is Perfect

When creating SBS 3D video from 2D, you need:
1. To know which parts are foreground/background ✅ (relative depth)
2. To create disparity (left/right eye offset) ✅ (relative depth)
3. To generate stereo effect ✅ (relative depth)

You **DO NOT** need:
- Actual distance in meters ❌
- Real-world scale measurements ❌
- Absolute depth values ❌

### How StereoPhotoMaker Works

StereoPhotoMaker uses the grayscale depth map to:
1. Identify depth layers (bright = close, dark = far)
2. Shift pixels based on depth (more shift = more depth)
3. Create left and right eye views
4. Combine into SBS 3D output

**It only needs relative depth relationships, not actual distances!**

---

## Common Misconception

"I need metric depth for better 3D quality" ❌

**Truth:** 3D quality depends on:
- ✅ Depth map accuracy (both models are good)
- ✅ Depth map resolution
- ✅ Consistent depth estimation across frames
- ✅ Proper grayscale output

Metric vs relative **doesn't affect 3D quality** for conversion purposes!

---

## When Metric Models Are Not Available

If you try `metric: true` and get an error:

```
FileNotFoundError: [Errno 2] No such file or directory:
'./checkpoints/metric_video_depth_anything_vitl.pth'
```

This means:
- Metric models are not publicly released on Hugging Face
- You need to use relative depth instead
- **This is totally fine for 3D conversion!**

**Solution:** Set `metric: false` in config.yaml

---

## Summary Table

| Feature | Relative Depth | Metric Depth |
|---------|---------------|--------------|
| **For 3D/SBS** | ✅ Perfect | ⚠️ Unnecessary |
| **Availability** | ✅ Always | ⚠️ May not be public |
| **Speed** | ✅ Fast | ≈ Same |
| **Quality for 3D** | ✅ Excellent | ≈ Same |
| **Robustness** | ✅ High | ⚠️ Dataset-specific |
| **Actual distances** | ❌ No | ✅ Yes |
| **StereoPhotoMaker** | ✅ Works great | ✅ Works (but overkill) |

---

## Recommended Configuration

For your 2D to 3D video workflow:

```yaml
# config.yaml
depth_settings:
  encoder: "vitl"        # Large model for quality
  metric: false          # Relative depth is perfect
  grayscale: true        # Required for 3D conversion
  fp32: false            # FP16 is faster
```

This gives you:
- ✅ High-quality depth maps
- ✅ Fast processing
- ✅ Perfect for SBS 3D conversion
- ✅ No model availability issues

---

## Still Want Metric Depth?

If your application truly requires actual distance measurements:

1. **Check if models are available:**
   ```bash
   cd Video-Depth-Anything/checkpoints
   ls -lh metric_*.pth
   ```

2. **Try downloading manually:**
   ```bash
   wget https://huggingface.co/depth-anything/Video-Depth-Anything-Large/resolve/main/metric_video_depth_anything_vitl.pth
   ```

3. **If download fails:**
   - Models are not publicly available
   - Contact the Video-Depth-Anything team
   - Or use relative depth for your application

---

## Bottom Line

**For 2D to 3D video conversion, use `metric: false`**

You'll get:
- Perfect depth maps for 3D
- Faster, more reliable processing
- No model availability issues
- Excellent SBS results with StereoPhotoMaker

The default config is already optimized for your needs!
