#!/bin/bash

# Solutions for OOM (Out Of Memory) kills during video encoding

echo "=========================================="
echo "OOM Fix Solutions"
echo "=========================================="
echo ""

echo "The process completed 100% of frame processing but was killed"
echo "during final video encoding due to insufficient RAM."
echo ""

# Check current situation
if [ -d "depth/PregnancyCravingsGoneWrongNew" ]; then
    frame_count=$(find depth/PregnancyCravingsGoneWrongNew -name "*.png" -o -name "*.jpg" 2>/dev/null | wc -l)

    if [ $frame_count -gt 0 ]; then
        echo "✓ Good news: $frame_count depth frames were successfully processed!"
        echo ""

        if [ ! -f "depth/PregnancyCravingsGoneWrongNew/depth_video.mp4" ]; then
            echo "Creating depth video from existing frames..."
            echo ""

            cd depth/PregnancyCravingsGoneWrongNew

            # Get frame rate from original video
            fps=$(ffprobe -v quiet -select_streams v:0 -show_entries stream=r_frame_rate -of csv=p=0 ../../in/PregnancyCravingsGoneWrongNew.mp4 2>/dev/null | head -1)

            if [ -z "$fps" ]; then
                fps="23.98"
                echo "Using default FPS: $fps"
            else
                echo "Detected FPS: $fps"
            fi

            # Check frame naming pattern
            if ls 00001.png &> /dev/null 2>&1; then
                pattern="%05d.png"
            elif ls frame_00001.png &> /dev/null 2>&1; then
                pattern="frame_%05d.png"
            else
                echo "Detecting frame pattern..."
                first_frame=$(find . -name "*.png" | head -1)
                echo "First frame: $first_frame"
                pattern="*.png"
            fi

            echo "Encoding video with pattern: $pattern"
            echo ""

            # Encode video with memory-efficient settings
            ffmpeg -y \
                -framerate "$fps" \
                -pattern_type glob -i "*.png" \
                -c:v libx264 \
                -preset medium \
                -crf 18 \
                -pix_fmt yuv420p \
                -movflags +faststart \
                depth_video.mp4

            if [ $? -eq 0 ]; then
                echo ""
                echo "=========================================="
                echo "✓ SUCCESS! Video created successfully!"
                echo "=========================================="
                ls -lh depth_video.mp4
                echo ""
                echo "Output: depth/PregnancyCravingsGoneWrongNew/depth_video.mp4"
                exit 0
            else
                echo ""
                echo "✗ FFmpeg encoding failed"
                echo "Try with lower quality settings (see below)"
            fi

            cd ../..
        else
            echo "✓ Video already exists!"
            ls -lh depth/PregnancyCravingsGoneWrongNew/depth_video.mp4
            exit 0
        fi
    fi
fi

echo ""
echo "=========================================="
echo "Prevention Solutions for Next Run"
echo "=========================================="
echo ""

echo "Option 1: Use smaller model (faster, less memory)"
echo "  Edit config.yaml:"
echo "    encoder: \"vits\"  # Change from vitl"
echo ""

echo "Option 2: Process shorter segments"
echo "  Edit config.yaml:"
echo "    max_len: 300  # Process first 5 minutes only"
echo ""

echo "Option 3: Reduce target FPS"
echo "  Edit config.yaml:"
echo "    target_fps: 15  # Fewer frames to encode"
echo ""

echo "Option 4: Upgrade RunPod instance"
echo "  Use instance with more RAM (32GB+ recommended)"
echo "  Current RAM: $(free -h | grep Mem | awk '{print $2}')"
echo ""

echo "Option 5: Add swap space (temporary fix)"
echo "  sudo fallocate -l 16G /swapfile"
echo "  sudo chmod 600 /swapfile"
echo "  sudo mkswap /swapfile"
echo "  sudo swapon /swapfile"
echo ""

echo "For now, if you have the frames, manually encode with:"
echo "  cd depth/PregnancyCravingsGoneWrongNew"
echo "  ffmpeg -framerate 23.98 -pattern_type glob -i '*.png' -c:v libx264 -crf 23 -pix_fmt yuv420p depth_video.mp4"
