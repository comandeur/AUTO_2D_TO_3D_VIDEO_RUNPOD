# Hardware Requirements Guide for RunPod

This guide helps you choose the right RunPod configuration for 2D to 3D video conversion.

## GPU Recommendations

### Recommended GPUs (Best Performance)

| GPU Model | VRAM | Model Support | Performance | Cost Efficiency |
|-----------|------|---------------|-------------|-----------------|
| **RTX 4090** | 24GB | Small + Large | Excellent | Best for most users |
| **A100 40GB** | 40GB | Small + Large | Excellent | Overkill but fastest |
| **A100 80GB** | 80GB | Small + Large | Excellent | Overkill, expensive |

### Budget-Friendly Options

| GPU Model | VRAM | Model Support | Performance | Notes |
|-----------|------|---------------|-------------|-------|
| **RTX 3090** | 24GB | Small + Large | Very Good | Great value |
| **RTX 3080** | 10GB | Small only | Good | Limited to small model |
| **RTX 4080** | 16GB | Small + Large* | Very Good | Large model may struggle with 4K |

*Large model works but may have memory issues with high-resolution videos

### VRAM Requirements by Model

**Small Model (vits - 28.4M parameters):**
- Checkpoint size: ~100 MB
- Runtime VRAM usage: 4-8 GB
- **Minimum GPU**: 8GB VRAM (RTX 3070, RTX 3080)
- **Recommended GPU**: 10-12GB VRAM (RTX 3080, RTX 3090)

**Large Model (vitl - 381.8M parameters):**
- Checkpoint size: ~700 MB
- Runtime VRAM usage: 12-20 GB
- **Minimum GPU**: 16GB VRAM (RTX 4080)
- **Recommended GPU**: 24GB VRAM (RTX 4090, RTX 3090, A100)

### Resolution Impact on VRAM

| Resolution | Small Model | Large Model |
|------------|-------------|-------------|
| 720p (1280x720) | 4-6 GB | 10-14 GB |
| 1080p (1920x1080) | 6-8 GB | 14-18 GB |
| 4K (3840x2160) | 10-12 GB | 20-24 GB |

### Our Recommendation

**For most users**: **RTX 4090 (24GB VRAM)**
- Handles both small and large models
- Processes 1080p and 4K videos comfortably
- Fast inference speed
- Good availability on RunPod
- Reasonable cost

**For budget users**: **RTX 3090 (24GB VRAM)**
- Same VRAM as 4090 but slightly slower
- Often cheaper on RunPod
- Perfectly adequate for most projects

**For testing/short videos**: **RTX 3080 (10GB VRAM)**
- Use small model only
- Stick to 1080p or lower resolution
- Most cost-effective option

## PyTorch Requirements

### Recommended PyTorch Version

```
PyTorch >= 2.0.0
CUDA >= 11.8 or >= 12.1
```

### RunPod Templates

Choose a RunPod template with:
- **PyTorch 2.0+** with CUDA support
- **Ubuntu 22.04** or newer
- **Python 3.8+** (Python 3.10 recommended)

**Recommended Templates on RunPod:**
1. **PyTorch 2.1.0** (CUDA 12.1)
2. **PyTorch 2.0.0** (CUDA 11.8)
3. **RunPod PyTorch** (latest stable)

The setup script will handle installing all Python dependencies automatically.

## Storage Requirements

### Breakdown

| Component | Size | Notes |
|-----------|------|-------|
| **Operating System** | 5-10 GB | Pre-installed on RunPod |
| **PyTorch + CUDA** | 5-7 GB | Included in templates |
| **Python Dependencies** | 2-3 GB | opencv, numpy, pillow, etc. |
| **Video-Depth-Anything Repo** | 100 MB | Cloned during setup |
| **Model Checkpoints** | | |
| - Small model | 100 MB | video_depth_anything_vits.pth |
| - Large model | 700 MB | video_depth_anything_vitl.pth |
| - Metric models (optional) | 800 MB | Both small + large metric |
| **Working Space** | Variable | For processing |
| **Input Videos** | Variable | Your 2D videos |
| **Output Videos** | Variable | ~1-2x input size |

### Storage Recommendations

**Minimum Configuration:**
- **30 GB** - For testing with small videos
  - System + dependencies: ~20 GB
  - 5 GB for videos (input + output)
  - 5 GB working space

**Recommended Configuration:**
- **100 GB** - For typical projects
  - System + dependencies: ~20 GB
  - 40 GB for videos
  - 40 GB working space

**Production Configuration:**
- **250-500 GB** - For large batches or long videos
  - System + dependencies: ~20 GB
  - 100-200 GB for videos
  - 130-280 GB working space

### Storage Type

**Container Disk** (Temporary):
- Cheaper
- Data lost when pod stops
- Good for: Testing, single-use processing

**Network Volume** (Persistent):
- More expensive but permanent
- Data persists when pod stops
- **Highly recommended** for:
  - Keeping model checkpoints (avoid re-downloading)
  - Storing processed videos
  - Long-term projects

## Cost Estimation (RunPod)

Approximate costs as of 2025 (prices vary by availability):

### Spot Instances (Cheapest)

| GPU | Typical Rate | 1 Hour | 10 Hours | Notes |
|-----|--------------|--------|----------|-------|
| RTX 3080 | $0.15-0.25/hr | $0.20 | $2.00 | Can be terminated |
| RTX 3090 | $0.25-0.35/hr | $0.30 | $3.00 | Can be terminated |
| RTX 4090 | $0.40-0.60/hr | $0.50 | $5.00 | Can be terminated |
| A100 40GB | $0.80-1.20/hr | $1.00 | $10.00 | Can be terminated |

### On-Demand (Reliable)

| GPU | Typical Rate | 1 Hour | 10 Hours | Notes |
|-----|--------------|--------|----------|-------|
| RTX 3090 | $0.50-0.70/hr | $0.60 | $6.00 | Guaranteed |
| RTX 4090 | $0.70-1.00/hr | $0.80 | $8.00 | Guaranteed |
| A100 40GB | $1.50-2.50/hr | $2.00 | $20.00 | Guaranteed |

**Recommendation**: Use **Spot Instances** for most work (50-70% cheaper)

## Processing Speed Estimates

Based on RTX 4090 (24GB VRAM):

### Small Model (vits)

| Video Length | Resolution | Processing Time | Cost (Spot @ $0.50/hr) |
|-------------|-----------|-----------------|------------------------|
| 30 seconds | 1080p | 2-3 minutes | $0.02 |
| 2 minutes | 1080p | 8-10 minutes | $0.08 |
| 5 minutes | 1080p | 20-25 minutes | $0.20 |
| 10 minutes | 1080p | 40-50 minutes | $0.40 |
| 30 seconds | 4K | 5-7 minutes | $0.05 |
| 2 minutes | 4K | 20-25 minutes | $0.20 |

### Large Model (vitl)

| Video Length | Resolution | Processing Time | Cost (Spot @ $0.50/hr) |
|-------------|-----------|-----------------|------------------------|
| 30 seconds | 1080p | 4-5 minutes | $0.04 |
| 2 minutes | 1080p | 15-20 minutes | $0.15 |
| 5 minutes | 1080p | 40-50 minutes | $0.40 |
| 10 minutes | 1080p | 80-100 minutes | $0.80 |
| 30 seconds | 4K | 10-15 minutes | $0.12 |
| 2 minutes | 4K | 40-50 minutes | $0.40 |

**Note**: Processing speed varies based on:
- Video FPS (30fps vs 60fps)
- Video complexity
- GPU temperature/throttling
- System load

## Recommended RunPod Configurations

### Configuration 1: Budget Testing
```
GPU: RTX 3080 (10GB)
Storage: 30GB Container Disk
Template: PyTorch 2.0 + CUDA 11.8
Model: Small (vits)
Use Case: Testing, short videos (<2 min), 1080p
Estimated Cost: ~$0.20/hour (spot)
```

### Configuration 2: Standard Production (RECOMMENDED)
```
GPU: RTX 4090 (24GB)
Storage: 100GB Container Disk or Network Volume
Template: PyTorch 2.1 + CUDA 12.1
Model: Large (vitl) or Small (vits)
Use Case: Most projects, 1080p and 4K
Estimated Cost: ~$0.50/hour (spot)
```

### Configuration 3: High-Volume Processing
```
GPU: RTX 4090 (24GB)
Storage: 250-500GB Network Volume
Template: PyTorch 2.1 + CUDA 12.1
Model: Large (vitl)
Use Case: Batch processing, long videos, 4K
Estimated Cost: ~$0.50/hour (spot) + storage
```

### Configuration 4: Maximum Performance
```
GPU: A100 40GB
Storage: 250-500GB Network Volume
Template: PyTorch 2.1 + CUDA 12.1
Model: Large (vitl)
Use Case: Very long videos, highest quality, 4K+
Estimated Cost: ~$1.00/hour (spot) + storage
```

## Quick Decision Guide

**Choose based on your needs:**

1. **"I want to test this first"**
   - GPU: RTX 3080 (10GB)
   - Storage: 30GB
   - Cost: ~$0.20/hr

2. **"I have several 1080p videos to process"**
   - GPU: RTX 4090 (24GB) ← **BEST CHOICE**
   - Storage: 100GB
   - Cost: ~$0.50/hr

3. **"I process videos regularly"**
   - GPU: RTX 4090 (24GB)
   - Storage: 250GB Network Volume (persistent)
   - Cost: ~$0.50/hr + storage

4. **"I need the absolute best quality and speed"**
   - GPU: A100 40GB
   - Storage: 500GB Network Volume
   - Cost: ~$1.00/hr + storage

## Tips to Minimize Costs

1. **Use Spot Instances**: 50-70% cheaper than on-demand
2. **Stop pods when not in use**: You're only charged when running
3. **Use Container Disk for one-time jobs**: Cheaper than network volumes
4. **Use Network Volume for repeated work**: Saves re-downloading models
5. **Process in batches**: Upload multiple videos, process all at once
6. **Start with Small Model**: 2x faster, good quality for most cases
7. **Monitor your pod**: Stop it as soon as processing is done

## Summary

**Our Top Recommendation for Most Users:**

```
GPU: RTX 4090 (24GB VRAM)
Storage: 100GB (Container Disk or Network Volume)
Template: PyTorch 2.1.0 with CUDA 12.1
Instance: Spot (for cost savings)
Estimated Cost: $0.40-0.60/hour
```

This configuration gives you:
- ✅ Support for both Small and Large models
- ✅ Handle 1080p and 4K videos
- ✅ Fast processing speeds
- ✅ Good value for money
- ✅ Widely available on RunPod

You can process a typical 2-minute 1080p video for **less than $0.10** using the large model!
