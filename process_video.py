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


def split_video_into_segments(video_path, segment_length, temp_dir):
    """Split video into segments of specified length (in seconds)"""
    print(f"\n{'='*80}")
    print(f"Splitting video into {segment_length}-second segments...")
    print(f"{'='*80}\n")

    # Get video duration
    video_info = get_video_info(video_path)
    if not video_info:
        print("ERROR: Could not get video info for segmentation")
        return []

    duration = video_info['duration']
    num_segments = int(duration / segment_length) + (1 if duration % segment_length > 0 else 0)

    print(f"Video duration: {duration:.2f}s ({duration/60:.1f} minutes)")
    print(f"Segment length: {segment_length}s ({segment_length/60:.1f} minutes)")
    print(f"Number of segments: {num_segments}\n")

    # Create temp directory for segments
    os.makedirs(temp_dir, exist_ok=True)

    segments = []
    for i in range(num_segments):
        start_time = i * segment_length
        segment_file = os.path.join(temp_dir, f"segment_{i:03d}.mp4")

        print(f"Creating segment {i+1}/{num_segments}: {start_time}s - {start_time+segment_length}s")

        # Use ffmpeg to extract segment
        cmd = [
            'ffmpeg',
            '-y',  # Overwrite
            '-ss', str(start_time),
            '-i', str(video_path),
            '-t', str(segment_length),
            '-c', 'copy',  # Copy codec (fast, no re-encoding)
            '-avoid_negative_ts', 'make_zero',
            segment_file
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0 and os.path.exists(segment_file):
            segments.append(Path(segment_file))
            print(f"  ✓ Created: {segment_file}")
        else:
            print(f"  ✗ Failed to create segment {i+1}")
            print(f"  Error: {result.stderr[:200]}")

    print(f"\n✓ Created {len(segments)} segments\n")
    return segments


def merge_depth_videos(segment_outputs, final_output_path, temp_dir):
    """Merge multiple depth video segments into one final video"""
    print(f"\n{'='*80}")
    print(f"Merging {len(segment_outputs)} depth video segments...")
    print(f"{'='*80}\n")

    # Create concat file list
    concat_file = os.path.join(temp_dir, 'concat_list.txt')

    with open(concat_file, 'w') as f:
        for segment_path in segment_outputs:
            # ffmpeg concat format requires file paths
            f.write(f"file '{os.path.abspath(segment_path)}'\n")

    print(f"Merge list created: {concat_file}")
    print(f"Output: {final_output_path}\n")

    # Merge using ffmpeg concat
    cmd = [
        'ffmpeg',
        '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', concat_file,
        '-c', 'copy',  # Copy codec (fast, no re-encoding)
        final_output_path
    ]

    print("Running ffmpeg merge...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0 and os.path.exists(final_output_path):
        file_size = os.path.getsize(final_output_path) / (1024 * 1024)  # MB
        print(f"\n✓ Successfully merged depth videos!")
        print(f"  Output: {final_output_path}")
        print(f"  Size: {file_size:.1f} MB\n")
        return True
    else:
        print(f"\n✗ Failed to merge videos")
        print(f"  Error: {result.stderr[:500]}\n")
        return False


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

    # Prepare output directory (use absolute path)
    video_output_dir = os.path.abspath(os.path.join(output_folder, video_path.stem))
    os.makedirs(video_output_dir, exist_ok=True)

    # Convert input video to absolute path
    input_video_abs = os.path.abspath(video_path)

    # Build command - choose between frame-saving mode or video encoding mode
    depth_settings = config['depth_settings']
    processing_settings = config['processing']
    save_frames_only = processing_settings.get('save_frames_only', True)

    # Use run_with_frame_saving.py if save_frames_only is enabled (default)
    # This saves individual PNG frames AND tries to encode video
    if save_frames_only:
        # Use our frame-saving wrapper (runs Video-Depth-Anything code but saves frames)
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'run_with_frame_saving.py'))
        cmd = [
            'python3',
            script_path,
            '--input_video', input_video_abs,
            '--output_dir', video_output_dir,
            '--encoder', depth_settings['encoder']
        ]
        print("[MODE] Saving individual frames (prevents data loss, allows local encoding)")
        print("  - Frames saved as PNG files during processing")
        print("  - Video encoding attempted (may fail with OOM, but frames are safe)")
    else:
        # Use original run.py for direct video encoding
        cmd = [
            'python3',
            'run.py',
            '--input_video', input_video_abs,
            '--output_dir', video_output_dir,
            '--encoder', depth_settings['encoder']
        ]
        print("[MODE] Encoding video directly (may cause OOM on long videos)")

    # Add optional parameters
    if depth_settings.get('metric'):
        cmd.append('--metric')

    if depth_settings.get('max_len', -1) != -1:
        cmd.extend(['--max_len', str(depth_settings['max_len'])])

    # Only add target_fps if explicitly set to a positive value
    # -1 means "use original fps" - don't pass parameter at all
    target_fps_value = depth_settings.get('target_fps', -1)
    if target_fps_value > 0:  # Only pass if it's a valid positive number
        cmd.extend(['--target_fps', str(target_fps_value)])

    if depth_settings.get('fp32'):
        cmd.append('--fp32')

    if depth_settings.get('grayscale'):
        cmd.append('--grayscale')

    # Determine working directory based on mode
    if save_frames_only:
        # Frame-saving mode: run from project root (where Video-Depth-Anything folder exists)
        work_dir = os.path.dirname(os.path.abspath(__file__))
        if not work_dir:  # If __file__ is not set, use current directory
            work_dir = os.path.abspath(os.getcwd())
    else:
        # Video encoding mode: run from Video-Depth-Anything directory (for relative paths)
        work_dir = os.path.abspath(vda_path)

    print(f"\nCommand: {' '.join(cmd)}")
    print(f"Working directory: {work_dir}")
    print(f"\nStarting conversion at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Output directory: {video_output_dir}\n")

    # Run the process
    start_time = time.time()

    try:
        # Set environment variables to disable xformers/flash-attention if they cause issues
        # This prevents CUDA compatibility errors with flash-attention
        env = os.environ.copy()
        env['XFORMERS_DISABLED'] = '1'
        env['XFORMERS_FORCE_DISABLE_TRITON'] = '1'

        # Fix CUDA memory fragmentation issue
        # Enables expandable memory segments to avoid fragmentation errors
        env['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'

        process = subprocess.Popen(
            cmd,
            cwd=work_dir,  # Set correct working directory based on mode
            env=env,  # Use modified environment with xformers disabled
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


def process_video_with_segmentation(video_file, config, vda_path, output_folder):
    """Process video with automatic segmentation if enabled"""
    processing_settings = config['processing']
    auto_segment = processing_settings.get('auto_segment', False)
    segment_length = processing_settings.get('segment_length', 300)

    if not auto_segment:
        # No segmentation - process video directly
        return process_video(video_file, config, vda_path, output_folder)

    # Auto-segmentation enabled
    print(f"\n{'='*80}")
    print(f"AUTO-SEGMENTATION MODE ENABLED")
    print(f"{'='*80}\n")

    # Create temp directory for segments
    temp_dir = os.path.join(output_folder, f".temp_{video_file.stem}")
    os.makedirs(temp_dir, exist_ok=True)

    try:
        # Step 1: Split video into segments
        segments = split_video_into_segments(video_file, segment_length, temp_dir)

        if not segments:
            print("ERROR: No segments created")
            return False

        # Step 2: Process each segment
        segment_depth_videos = []
        successful_segments = 0

        for i, segment in enumerate(segments):
            print(f"\n{'='*80}")
            print(f"Processing Segment {i+1}/{len(segments)}")
            print(f"{'='*80}\n")

            # Process this segment
            segment_output_dir = os.path.join(temp_dir, f"segment_{i:03d}_output")

            if process_video(segment, config, vda_path, segment_output_dir):
                successful_segments += 1

                # Find the depth video output
                depth_video = None
                if processing_settings.get('save_frames_only', True):
                    # Frame-saving mode - find the depth video
                    depth_video = os.path.join(segment_output_dir, f"segment_{i:03d}_depth.mp4")
                    # Also check for other naming patterns
                    if not os.path.exists(depth_video):
                        for f in os.listdir(segment_output_dir):
                            if f.endswith('_depth.mp4') or f.endswith('_vis.mp4'):
                                depth_video = os.path.join(segment_output_dir, f)
                                break
                else:
                    # Direct encoding mode
                    for f in os.listdir(segment_output_dir):
                        if '_depth.mp4' in f or '_vis.mp4' in f:
                            depth_video = os.path.join(segment_output_dir, f)
                            break

                if depth_video and os.path.exists(depth_video):
                    segment_depth_videos.append(depth_video)
                    print(f"✓ Segment {i+1} depth video: {depth_video}")
                else:
                    print(f"⚠ Warning: Depth video not found for segment {i+1}")
            else:
                print(f"✗ Failed to process segment {i+1}")

        # Step 3: Merge depth videos
        if len(segment_depth_videos) == len(segments):
            print(f"\n✓ All {len(segments)} segments processed successfully!")

            # Create final output path
            final_depth_video = os.path.join(output_folder, video_file.stem, f"{video_file.stem}_depth_full.mp4")
            os.makedirs(os.path.dirname(final_depth_video), exist_ok=True)

            if merge_depth_videos(segment_depth_videos, final_depth_video, temp_dir):
                print(f"\n{'='*80}")
                print(f"SUCCESS: Auto-segmentation complete!")
                print(f"{'='*80}")
                print(f"Final depth video: {final_depth_video}")
                print(f"Segments processed: {successful_segments}/{len(segments)}")
                print(f"{'='*80}\n")

                # Cleanup temp files if successful
                print("Cleaning up temporary files...")
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
                print("✓ Cleanup complete\n")

                return True
            else:
                print("ERROR: Failed to merge depth videos")
                return False
        else:
            print(f"\n✗ Only {len(segment_depth_videos)}/{len(segments)} segments succeeded")
            print("Cannot merge incomplete results")
            return False

    except Exception as e:
        print(f"\nERROR during auto-segmentation: {e}")
        import traceback
        traceback.print_exc()
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

    # Check if auto-segmentation is enabled
    if config['processing'].get('auto_segment', False):
        print(f"\n🎬 Auto-segmentation: ENABLED")
        print(f"   Segment length: {config['processing'].get('segment_length', 300)} seconds")
    else:
        print(f"\n🎬 Auto-segmentation: DISABLED")

    # Process videos
    successful = 0
    failed = 0

    total_start_time = time.time()

    for video_file in video_files:
        if process_video_with_segmentation(video_file, config, vda_path, output_folder):
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
