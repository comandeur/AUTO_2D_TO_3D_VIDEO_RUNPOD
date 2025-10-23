#!/usr/bin/env python3
"""
2D to 3D Video Conversion Automation Script
Processes videos using Video-Depth-Anything for depth estimation
"""

import os
import sys
import yaml
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime, timedelta


def load_config(config_path="config.yaml"):
    """Load configuration from YAML file"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def check_video_depth_anything_setup(vda_path):
    """Check if Video-Depth-Anything is properly set up"""
    if not os.path.exists(vda_path):
        print(f"ERROR: Video-Depth-Anything not found at {vda_path}")
        print("Please run setup_runpod.sh first to clone and set up the repository")
        return False

    run_script = os.path.join(vda_path, "run.py")
    if not os.path.exists(run_script):
        print(f"ERROR: run.py not found in {vda_path}")
        return False

    checkpoints_dir = os.path.join(vda_path, "checkpoints")
    if not os.path.exists(checkpoints_dir):
        print(f"ERROR: checkpoints directory not found at {checkpoints_dir}")
        print("Please run ./download_models.sh to download model checkpoints")
        return False

    return True


def check_model_checkpoints(vda_path, encoder, metric=False):
    """Check if required model checkpoints exist"""
    checkpoints_dir = os.path.join(vda_path, "checkpoints")

    # Determine checkpoint filename based on settings
    if metric:
        checkpoint_file = f"metric_video_depth_anything_{encoder}.pth"
    else:
        checkpoint_file = f"video_depth_anything_{encoder}.pth"

    checkpoint_path = os.path.join(checkpoints_dir, checkpoint_file)

    if not os.path.exists(checkpoint_path):
        print(f"\n{'='*80}")
        print(f"ERROR: Model checkpoint not found!")
        print(f"{'='*80}")
        print(f"Missing file: {checkpoint_file}")
        print(f"Expected location: {checkpoint_path}")
        print(f"\nConfiguration:")
        print(f"  encoder: {encoder}")
        print(f"  metric: {metric}")
        print(f"\nRequired checkpoint: {checkpoint_file}")
        print(f"\n{'='*80}")
        print(f"SOLUTION:")
        print(f"{'='*80}")
        print(f"\n1. Run the model download script:")
        print(f"   ./download_models.sh")
        print(f"\n2. Or download manually:")
        if encoder == "vits":
            model_url = "https://huggingface.co/depth-anything/Video-Depth-Anything-Small/resolve/main/video_depth_anything_vits.pth"
            print(f"   wget -P {checkpoints_dir} {model_url}")
        else:  # vitl
            model_url = "https://huggingface.co/depth-anything/Video-Depth-Anything-Large/resolve/main/video_depth_anything_vitl.pth"
            print(f"   wget -P {checkpoints_dir} {model_url}")

        if metric:
            print(f"\nNOTE: You have metric: true in config.yaml")
            print(f"Metric models may not be publicly available.")
            print(f"For 3D conversion, set metric: false in config.yaml")

        print(f"\n{'='*80}\n")
        return False

    # Checkpoint exists, show info
    file_size = os.path.getsize(checkpoint_path) / (1024 * 1024)  # Convert to MB
    print(f"✓ Model checkpoint found: {checkpoint_file} ({file_size:.1f} MB)")

    return True


def get_video_files(input_folder):
    """Get all video files from input folder"""
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv']
    video_files = []

    for ext in video_extensions:
        video_files.extend(Path(input_folder).glob(f"*{ext}"))
        video_files.extend(Path(input_folder).glob(f"*{ext.upper()}"))

    return sorted(video_files)


def get_video_info(video_path):
    """Get video information using ffprobe"""
    try:
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            str(video_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        info = json.loads(result.stdout)

        # Find video stream
        video_stream = None
        for stream in info.get('streams', []):
            if stream.get('codec_type') == 'video':
                video_stream = stream
                break

        if video_stream:
            # Calculate total frames
            duration = float(info['format'].get('duration', 0))
            fps_str = video_stream.get('r_frame_rate', '30/1')
            fps_num, fps_den = map(int, fps_str.split('/'))
            fps = fps_num / fps_den
            total_frames = int(duration * fps)

            return {
                'duration': duration,
                'fps': fps,
                'total_frames': total_frames,
                'width': video_stream.get('width'),
                'height': video_stream.get('height')
            }
    except Exception as e:
        print(f"Warning: Could not get video info: {e}")

    return None


def process_video(video_path, config, vda_path, output_folder):
    """Process a single video file"""
    print(f"\n{'='*80}")
    print(f"Processing: {video_path.name}")
    print(f"{'='*80}")

    # Get video info
    video_info = get_video_info(video_path)
    if video_info:
        print(f"Video info:")
        print(f"  Duration: {video_info['duration']:.2f}s")
        print(f"  FPS: {video_info['fps']:.2f}")
        print(f"  Total frames: {video_info['total_frames']}")
        print(f"  Resolution: {video_info['width']}x{video_info['height']}")

    # Prepare output directory
    video_output_dir = os.path.join(output_folder, video_path.stem)
    os.makedirs(video_output_dir, exist_ok=True)

    # Build command
    depth_settings = config['depth_settings']
    cmd = [
        'python3',
        os.path.join(vda_path, 'run.py'),
        '--input_video', str(video_path),
        '--output_dir', video_output_dir,
        '--encoder', depth_settings['encoder']
    ]

    # Add optional parameters
    if depth_settings.get('metric'):
        cmd.append('--metric')

    if depth_settings.get('max_len', -1) != -1:
        cmd.extend(['--max_len', str(depth_settings['max_len'])])

    if depth_settings.get('target_fps', -1) != -1:
        cmd.extend(['--target_fps', str(depth_settings['target_fps'])])

    if depth_settings.get('fp32'):
        cmd.append('--fp32')

    if depth_settings.get('grayscale'):
        cmd.append('--grayscale')

    print(f"\nCommand: {' '.join(cmd)}")
    print(f"\nStarting conversion at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Output directory: {video_output_dir}\n")

    # Run the process
    start_time = time.time()

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )

        # Monitor output for progress
        frame_count = 0
        for line in process.stdout:
            print(line, end='')

            # Try to extract frame information from output
            # (Video-Depth-Anything may output progress info)
            if 'frame' in line.lower() or 'processing' in line.lower():
                frame_count += 1

                # Show progress every N frames
                if frame_count % config['processing'].get('progress_update_frequency', 10) == 0:
                    elapsed = time.time() - start_time
                    if video_info and video_info['total_frames'] > 0:
                        progress = (frame_count / video_info['total_frames']) * 100
                        eta = (elapsed / frame_count) * (video_info['total_frames'] - frame_count)
                        print(f"[PROGRESS] Frames: {frame_count}/{video_info['total_frames']} "
                              f"({progress:.1f}%) | Elapsed: {str(timedelta(seconds=int(elapsed)))} | "
                              f"ETA: {str(timedelta(seconds=int(eta)))}")
                    else:
                        print(f"[PROGRESS] Frames processed: {frame_count} | "
                              f"Elapsed: {str(timedelta(seconds=int(elapsed)))}")

        process.wait()

        elapsed_time = time.time() - start_time

        if process.returncode == 0:
            print(f"\n{'='*80}")
            print(f"SUCCESS: Video processed in {str(timedelta(seconds=int(elapsed_time)))}")
            print(f"Output saved to: {video_output_dir}")
            print(f"{'='*80}\n")
            return True
        else:
            print(f"\nERROR: Process failed with return code {process.returncode}")
            return False

    except Exception as e:
        print(f"\nERROR: {e}")
        return False


def main():
    """Main execution function"""
    print("="*80)
    print("2D to 3D Video Conversion - Depth Estimation")
    print("="*80)

    # Load configuration
    try:
        config = load_config()
        print("\nConfiguration loaded successfully")
    except Exception as e:
        print(f"ERROR: Failed to load config.yaml: {e}")
        sys.exit(1)

    # Get paths from config
    paths = config['paths']
    input_folder = paths['input_folder']
    output_folder = paths['depth_output_folder']
    vda_path = paths['video_depth_anything_folder']

    # Check Video-Depth-Anything setup
    if not check_video_depth_anything_setup(vda_path):
        sys.exit(1)

    # Check model checkpoints exist before processing
    depth_settings = config['depth_settings']
    encoder = depth_settings.get('encoder', 'vitl')
    metric = depth_settings.get('metric', False)

    print(f"\nVerifying model checkpoints...")
    print(f"Model configuration: encoder={encoder}, metric={metric}")

    if not check_model_checkpoints(vda_path, encoder, metric):
        sys.exit(1)

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Get videos to process
    if config['processing'].get('batch_process', True):
        video_files = get_video_files(input_folder)
        if not video_files:
            print(f"\nNo video files found in {input_folder}")
            print("Supported formats: .mp4, .avi, .mov, .mkv, .webm, .flv")
            sys.exit(1)
        print(f"\nFound {len(video_files)} video(s) to process:")
        for vf in video_files:
            print(f"  - {vf.name}")
    else:
        single_file = config['processing'].get('single_video_file')
        if not single_file:
            print("ERROR: single_video_file not specified in config")
            sys.exit(1)
        video_files = [Path(input_folder) / single_file]
        if not video_files[0].exists():
            print(f"ERROR: Video file not found: {video_files[0]}")
            sys.exit(1)

    # Process videos
    successful = 0
    failed = 0

    total_start_time = time.time()

    for video_file in video_files:
        if process_video(video_file, config, vda_path, output_folder):
            successful += 1
        else:
            failed += 1

    total_elapsed = time.time() - total_start_time

    # Summary
    print("\n" + "="*80)
    print("PROCESSING SUMMARY")
    print("="*80)
    print(f"Total videos processed: {len(video_files)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total time: {str(timedelta(seconds=int(total_elapsed)))}")
    print("="*80)

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
