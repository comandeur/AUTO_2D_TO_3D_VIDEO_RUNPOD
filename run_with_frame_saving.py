#!/usr/bin/env python3
"""
Wrapper that runs Video-Depth-Anything but saves individual frames
by monkey-patching the save_video function.
"""

import os
import sys

# Find Video-Depth-Anything directory
vda_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Video-Depth-Anything')

if not os.path.exists(vda_dir):
    print(f"ERROR: Video-Depth-Anything directory not found at {vda_dir}")
    print("Please run setup_runpod.sh first")
    sys.exit(1)

print(f"Video-Depth-Anything directory: {vda_dir}")

# Ensure both utils and video_depth_anything have __init__.py
# Video-Depth-Anything repo is missing these files!
for subdir in ['utils', 'video_depth_anything']:
    init_file = os.path.join(vda_dir, subdir, '__init__.py')
    if not os.path.exists(init_file):
        print(f"Creating missing __init__.py in {subdir}/ ...")
        open(init_file, 'a').close()

# Add to Python path AND change directory
sys.path.insert(0, vda_dir)
os.chdir(vda_dir)

print(f"Current directory: {os.getcwd()}")
print(f"Python path includes: {vda_dir}")

# Now import - should work because we're in the directory AND it's in sys.path
import numpy as np
import imageio
import argparse
import torch

# Import Video-Depth-Anything modules
try:
    from utils.dc_utils import read_video_frames
    from video_depth_anything import VideoDepthAnything
    print("✓ Successfully imported Video-Depth-Anything modules")
except ImportError as e:
    print(f"ERROR: Import failed: {e}")
    print(f"Current directory: {os.getcwd()}")
    print(f"sys.path: {sys.path[:3]}")
    print(f"\nChecking if files exist:")
    print(f"  utils/dc_utils.py: {os.path.exists('utils/dc_utils.py')}")
    print(f"  video_depth_anything/__init__.py: {os.path.exists('video_depth_anything/__init__.py')}")
    sys.exit(1)

# Global variable to store output directory
FRAME_OUTPUT_DIR = None


def save_video_with_frames(frames, output_video_path, fps=10, is_depths=False, grayscale=False):
    """
    Modified save_video that saves individual frames AND creates video
    """
    import matplotlib.cm as cm

    print(f"\n{'='*80}")
    print(f"Saving frames to disk...")
    print(f"{'='*80}\n")

    # Create frames directory
    if FRAME_OUTPUT_DIR:
        if is_depths:
            frames_dir = os.path.join(FRAME_OUTPUT_DIR, "depth_frames")
        else:
            frames_dir = os.path.join(FRAME_OUTPUT_DIR, "source_frames")

        os.makedirs(frames_dir, exist_ok=True)

        print(f"Saving {len(frames)} frames to: {frames_dir}/")

        # Save frames
        if is_depths:
            colormap = np.array(cm.get_cmap("inferno").colors)
            d_min, d_max = frames.min(), frames.max()

            for i in range(frames.shape[0]):
                depth = frames[i]
                depth_norm = ((depth - d_min) / (d_max - d_min) * 255).astype(np.uint8)

                if grayscale:
                    frame_to_save = depth_norm
                else:
                    frame_to_save = (colormap[depth_norm] * 255).astype(np.uint8)

                frame_path = os.path.join(frames_dir, f"{i:05d}.png")
                imageio.imwrite(frame_path, frame_to_save)

                if i % 100 == 0:
                    print(f"  Saved {i}/{len(frames)} frames...")
        else:
            for i in range(frames.shape[0]):
                frame_path = os.path.join(frames_dir, f"{i:05d}.png")
                imageio.imwrite(frame_path, frames[i])

                if i % 100 == 0:
                    print(f"  Saved {i}/{len(frames)} frames...")

        print(f"\n✓ All {len(frames)} frames saved!\n")

        # Save metadata
        metadata_path = os.path.join(FRAME_OUTPUT_DIR, "metadata.txt")
        with open(metadata_path, 'w') as f:
            f.write(f"total_frames: {len(frames)}\n")
            f.write(f"fps: {fps}\n")
            f.write(f"frame_naming: %05d.png\n")
            f.write(f"grayscale: {grayscale}\n")

    # Now create video (may fail with OOM, but frames are already saved!)
    print(f"Creating video (if this fails with OOM, frames are already saved): {output_video_path}")

    try:
        writer = imageio.get_writer(output_video_path, fps=fps, macro_block_size=1,
                                     codec='libx264', ffmpeg_params=['-crf', '18'])

        if is_depths:
            colormap = np.array(cm.get_cmap("inferno").colors)
            d_min, d_max = frames.min(), frames.max()
            for i in range(frames.shape[0]):
                depth = frames[i]
                depth_norm = ((depth - d_min) / (d_max - d_min) * 255).astype(np.uint8)
                depth_vis = (colormap[depth_norm] * 255).astype(np.uint8) if not grayscale else depth_norm
                writer.append_data(depth_vis)
        else:
            for i in range(frames.shape[0]):
                writer.append_data(frames[i])

        writer.close()
        print(f"✓ Video created successfully: {output_video_path}")
    except Exception as e:
        print(f"\n⚠ Video encoding failed (OOM likely), but frames are saved!")
        print(f"Error: {e}")
        print(f"\nFrames location: {frames_dir if FRAME_OUTPUT_DIR else 'N/A'}")
        print(f"Download frames and encode locally with:")
        print(f"  cd {frames_dir if FRAME_OUTPUT_DIR else 'depth_frames'}")
        print(f"  ffmpeg -framerate {fps} -i %05d.png -c:v libx264 -crf 18 -pix_fmt yuv420p depth_video.mp4")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_video', type=str, required=True)
    parser.add_argument('--output_dir', type=str, required=True)
    parser.add_argument('--encoder', type=str, default='vitl', choices=['vits', 'vitl'])
    parser.add_argument('--max_len', type=int, default=-1)
    parser.add_argument('--target_fps', type=float, default=-1)
    parser.add_argument('--max_res', type=int, default=1024)
    parser.add_argument('--input_size', type=int, default=392)
    parser.add_argument('--fp32', action='store_true')
    parser.add_argument('--grayscale', action='store_true')
    parser.add_argument('--metric', action='store_true')
    args = parser.parse_args()

    # Set global output directory for frame saving
    FRAME_OUTPUT_DIR = args.output_dir

    # Monkey-patch the save_video function
    import utils.dc_utils
    utils.dc_utils.save_video = save_video_with_frames

    # Now run the normal Video-Depth-Anything code
    DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

    print(f"Device: {DEVICE}")
    if DEVICE == 'cuda':
        print(f"GPU: {torch.cuda.get_device_name(0)}")

    # Load model
    if args.metric:
        checkpoint_name = f"metric_video_depth_anything_{args.encoder}.pth"
    else:
        checkpoint_name = f"video_depth_anything_{args.encoder}.pth"

    checkpoint_path = os.path.join('checkpoints', checkpoint_name)

    if not os.path.exists(checkpoint_path):
        print(f"ERROR: Checkpoint not found: {checkpoint_path}")
        sys.exit(1)

    print(f"Loading model: {args.encoder}")
    video_depth_anything = VideoDepthAnything(encoder=args.encoder)
    video_depth_anything.load_state_dict(torch.load(checkpoint_path, map_location='cpu'))
    video_depth_anything = video_depth_anything.to(DEVICE).eval()

    # Read video
    print(f"\nReading video: {args.input_video}")
    frames, target_fps = read_video_frames(args.input_video, args.max_len, args.target_fps, args.max_res)
    print(f"Frames: {len(frames)}, FPS: {target_fps}")

    # Process depth
    print(f"\nProcessing depth...")
    depths, fps = video_depth_anything.infer_video_depth(
        frames, target_fps, input_size=args.input_size, device=DEVICE, fp32=args.fp32
    )

    print(f"\n✓ Depth processing complete!")

    # Save outputs (using our patched function that saves frames)
    video_name = os.path.basename(args.input_video)
    os.makedirs(args.output_dir, exist_ok=True)

    processed_video_path = os.path.join(args.output_dir, os.path.splitext(video_name)[0]+'_src.mp4')
    depth_vis_path = os.path.join(args.output_dir, os.path.splitext(video_name)[0]+'_depth.mp4')

    # This will save frames AND try to create video
    save_video_with_frames(frames, processed_video_path, fps=fps, is_depths=False, grayscale=False)
    save_video_with_frames(depths, depth_vis_path, fps=fps, is_depths=True, grayscale=args.grayscale)

    print(f"\n{'='*80}")
    print(f"COMPLETE!")
    print(f"{'='*80}")
    print(f"\nOutput directory: {args.output_dir}")
    print(f"  - depth_frames/: Individual depth PNG files")
    print(f"  - source_frames/: Individual source PNG files")
    print(f"  - metadata.txt: Video info")
    print(f"\nTo package for download:")
    print(f"  ./package_frames.sh")
