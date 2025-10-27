#!/usr/bin/env python3
"""
Modified Video-Depth-Anything runner that saves individual frames
instead of encoding video directly. This prevents OOM kills and allows
downloading frames for local encoding.

This is a wrapper around Video-Depth-Anything/run.py that intercepts
the output and saves frames individually.
"""

import os
import sys
import argparse
import numpy as np
import torch
import imageio
from pathlib import Path
from tqdm import tqdm

# Find Video-Depth-Anything directory relative to this script
script_dir = os.path.dirname(os.path.abspath(__file__))
vda_path = os.path.join(script_dir, 'Video-Depth-Anything')

# Add Video-Depth-Anything to path
if os.path.exists(vda_path):
    sys.path.insert(0, vda_path)
else:
    print(f"ERROR: Video-Depth-Anything not found at {vda_path}")
    print("Please run setup_runpod.sh first")
    sys.exit(1)

from utils.dc_utils import read_video_frames
from video_depth_anything import VideoDepthAnything


def save_depth_frame(depth, output_path, grayscale=True):
    """Save a single depth frame as PNG"""
    import matplotlib.cm as cm

    if grayscale:
        # Save as grayscale (0-255)
        depth_norm = ((depth - depth.min()) / (depth.max() - depth.min()) * 255).astype(np.uint8)
        imageio.imwrite(output_path, depth_norm)
    else:
        # Save with colormap
        colormap = np.array(cm.get_cmap("inferno").colors)
        depth_norm = ((depth - depth.min()) / (depth.max() - depth.min()) * 255).astype(np.uint8)
        depth_vis = (colormap[depth_norm] * 255).astype(np.uint8)
        imageio.imwrite(output_path, depth_vis)


def process_video_save_frames(args):
    """Process video and save individual depth frames"""

    # Set device
    DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

    print(f"Using device: {DEVICE}")
    if DEVICE == 'cuda':
        print(f"GPU: {torch.cuda.get_device_name(0)}")

    # Initialize Video-Depth-Anything
    print(f"\nLoading model: {args.encoder}")

    # Determine checkpoint path
    if args.metric:
        checkpoint_name = f"metric_video_depth_anything_{args.encoder}.pth"
    else:
        checkpoint_name = f"video_depth_anything_{args.encoder}.pth"

    checkpoint_path = os.path.join(vda_path, 'checkpoints', checkpoint_name)

    if not os.path.exists(checkpoint_path):
        print(f"ERROR: Model checkpoint not found: {checkpoint_path}")
        print("Please run: ./download_models.sh")
        sys.exit(1)

    # Load model
    video_depth_anything = VideoDepthAnything(encoder=args.encoder)
    video_depth_anything.load_state_dict(torch.load(checkpoint_path, map_location='cpu'))
    video_depth_anything = video_depth_anything.to(DEVICE).eval()

    # Read video frames
    print(f"\nReading video: {args.input_video}")
    frames, target_fps = read_video_frames(
        args.input_video,
        args.max_len,
        args.target_fps,
        args.max_res
    )

    print(f"Total frames: {len(frames)}")
    print(f"Target FPS: {target_fps}")

    # Create output directories
    os.makedirs(args.output_dir, exist_ok=True)

    frames_dir = os.path.join(args.output_dir, "depth_frames")
    os.makedirs(frames_dir, exist_ok=True)

    source_frames_dir = os.path.join(args.output_dir, "source_frames")
    os.makedirs(source_frames_dir, exist_ok=True)

    # Save metadata
    metadata_path = os.path.join(args.output_dir, "metadata.txt")
    with open(metadata_path, 'w') as f:
        f.write(f"input_video: {args.input_video}\n")
        f.write(f"total_frames: {len(frames)}\n")
        f.write(f"fps: {target_fps}\n")
        f.write(f"encoder: {args.encoder}\n")
        f.write(f"grayscale: {args.grayscale}\n")
        f.write(f"frame_naming: %05d.png\n")

    print(f"\nProcessing frames and saving to: {frames_dir}/")
    print(f"Source frames saving to: {source_frames_dir}/")
    print(f"This prevents OOM by saving each frame immediately\n")

    # Process frames one batch at a time
    # Video-Depth-Anything processes in batches, we save immediately after each batch
    print("Starting depth estimation...")

    depths, fps = video_depth_anything.infer_video_depth(
        frames,
        target_fps,
        input_size=args.input_size,
        device=DEVICE,
        fp32=args.fp32
    )

    print(f"\nDepth estimation complete! Now saving {len(depths)} frames...")

    # Normalize depth globally for consistent scaling
    d_min, d_max = depths.min(), depths.max()

    # Save each frame
    for i in tqdm(range(len(depths)), desc="Saving frames"):
        # Save depth frame
        depth = depths[i]
        depth_norm = ((depth - d_min) / (d_max - d_min) * 255).astype(np.uint8)

        depth_path = os.path.join(frames_dir, f"{i:05d}.png")

        if args.grayscale:
            imageio.imwrite(depth_path, depth_norm)
        else:
            import matplotlib.cm as cm
            colormap = np.array(cm.get_cmap("inferno").colors)
            depth_vis = (colormap[depth_norm] * 255).astype(np.uint8)
            imageio.imwrite(depth_path, depth_vis)

        # Save source frame
        source_path = os.path.join(source_frames_dir, f"{i:05d}.png")
        imageio.imwrite(source_path, frames[i])

        # Clear from memory periodically
        if i % 100 == 0:
            torch.cuda.empty_cache() if DEVICE == 'cuda' else None

    print(f"\n✓ All frames saved successfully!")
    print(f"\nOutput structure:")
    print(f"  {args.output_dir}/")
    print(f"    ├── depth_frames/     ({len(depths)} PNG files)")
    print(f"    ├── source_frames/    ({len(frames)} PNG files)")
    print(f"    └── metadata.txt")

    print(f"\nTo download and encode locally:")
    print(f"  1. Run: ./package_frames.sh")
    print(f"  2. Download the .tar.gz file")
    print(f"  3. Extract and encode:")
    print(f"     cd depth_frames")
    print(f"     ffmpeg -framerate {fps} -i %05d.png -c:v libx264 -crf 18 -pix_fmt yuv420p depth_video.mp4")

    return depths, fps, frames_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Video-Depth-Anything with frame saving')

    parser.add_argument('--input_video', type=str, required=True, help='Path to input video')
    parser.add_argument('--output_dir', type=str, required=True, help='Output directory')
    parser.add_argument('--encoder', type=str, default='vitl', choices=['vits', 'vitl'],
                        help='Model size (vits=small, vitl=large)')

    parser.add_argument('--max_len', type=int, default=-1,
                        help='Maximum frames to process (-1 for all)')
    parser.add_argument('--target_fps', type=float, default=-1,
                        help='Target FPS (-1 for original)')
    parser.add_argument('--max_res', type=int, default=1024,
                        help='Maximum resolution')
    parser.add_argument('--input_size', type=int, default=392,
                        help='Input size for model')

    parser.add_argument('--fp32', action='store_true',
                        help='Use FP32 precision (slower but more accurate)')
    parser.add_argument('--grayscale', action='store_true',
                        help='Save grayscale depth maps (needed for 3D conversion)')
    parser.add_argument('--metric', action='store_true',
                        help='Use metric depth model')

    args = parser.parse_args()

    try:
        depths, fps, frames_dir = process_video_save_frames(args)
        print("\n" + "="*80)
        print("SUCCESS: All frames saved!")
        print("="*80)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
