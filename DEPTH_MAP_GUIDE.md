# Depth Map Output Guide

## Understanding Depth Maps

Video-Depth-Anything can output depth maps in two formats:

### 1. Grayscale Depth Maps (Recommended for 3D Conversion)

**What it is:**
- Pure depth information where pixel brightness = depth value
- Brighter pixels = closer to camera
- Darker pixels = farther from camera
- Values typically range from 0-255 (8-bit) or 0.0-1.0 (normalized)

**When to use:**
- ✅ **3D/SBS conversion** (StereoPhotoMaker, other stereo tools)
- ✅ **Depth-based effects** (bokeh, refocusing)
- ✅ **3D reconstruction**
- ✅ **Computer vision applications**

**Configuration:**
```yaml
depth_settings:
  grayscale: true  # Default for 3D conversion
```

**File output:**
- `depth_video.mp4` - Grayscale video with pure depth values
- Can be directly used by StereoPhotoMaker and similar tools

---

### 2. Colorized Depth Maps (For Visualization Only)

**What it is:**
- Depth values mapped to a color palette (like "inferno" or "viridis")
- Colors make it easier for humans to see depth variations
- **NOT suitable for 3D conversion** - colors don't represent actual depth values

**When to use:**
- 👁️ **Visualization and demonstration**
- 👁️ **Human review of depth quality**
- 👁️ **Presentations and portfolios**
- ❌ **NOT for 3D/SBS conversion**

**Configuration:**
```yaml
depth_settings:
  grayscale: false  # Only use for visualization
```

**File output:**
- `depth_video.mp4` - Colorful video with color-mapped depth
- Looks nicer but cannot be used for 3D conversion

---

## Why Grayscale for 3D Conversion?

StereoPhotoMaker and other 3D conversion tools need **pure depth values** to:

1. **Calculate disparity**: Determine how far to shift pixels left/right for stereo effect
2. **Create left/right views**: Generate the two images needed for 3D
3. **Maintain depth accuracy**: Color palettes obscure the actual depth information

### Example Workflow

**For 3D/SBS Output (Your Use Case):**
```
2D Video → Depth Estimation (grayscale) → StereoPhotoMaker → SBS 3D Video
```

**For Visualization:**
```
2D Video → Depth Estimation (colorized) → Share on social media
```

---

## Current Configuration

The default `config.yaml` is set to:

```yaml
depth_settings:
  grayscale: true  # ✅ Correct for 3D conversion
```

This ensures your depth maps are ready for StereoPhotoMaker conversion to SBS 3D video.

---

## Visual Comparison

### Grayscale Depth Map
```
White (255) = Very close to camera
Gray (127)  = Medium distance
Black (0)   = Far from camera
```

### Colorized Depth Map (Example: Inferno palette)
```
Yellow/White = Close
Red/Orange   = Medium
Purple/Black = Far
```

While the colorized version looks more appealing, the grayscale version contains the actual depth data needed for conversion.

---

## Switching Between Formats

If you want **both** formats, you can:

1. Run once with `grayscale: true` (for 3D conversion)
2. Run again with `grayscale: false` (for visualization)

However, for your use case (3D/SBS conversion), you only need the grayscale version.

---

## Summary

**For your 2D to 3D workflow:**

✅ **Use:** `grayscale: true` (default)
✅ **Output:** Pure depth values for StereoPhotoMaker
✅ **Result:** High-quality SBS 3D video

The configuration is already optimized for your needs!
