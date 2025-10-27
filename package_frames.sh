#!/bin/bash

# Package processed depth frames for download

echo "=========================================="
echo "Package Depth Frames for Download"
echo "=========================================="
echo ""

OUTPUT_DIR="depth/PregnancyCravingsGoneWrongNew"

if [ ! -d "$OUTPUT_DIR" ]; then
    echo "✗ Output directory not found: $OUTPUT_DIR"
    echo "Checking for other possible locations..."
    find depth -type d 2>/dev/null | head -10
    exit 1
fi

# Check for new structure (depth_frames/) or old structure (loose files)
FRAMES_DIR="$OUTPUT_DIR/depth_frames"
if [ -d "$FRAMES_DIR" ]; then
    echo "✓ Found frame-saving mode output structure"
    SEARCH_DIR="$FRAMES_DIR"
else
    echo "Checking for old-style output (direct video encoding)..."
    SEARCH_DIR="$OUTPUT_DIR"
fi

# Count frames
frame_count=$(find "$SEARCH_DIR" -name "*.png" -o -name "*.jpg" 2>/dev/null | wc -l)

if [ $frame_count -eq 0 ]; then
    echo "✗ No frames found in $OUTPUT_DIR"
    ls -la "$OUTPUT_DIR"
    exit 1
fi

echo "✓ Found $frame_count depth frames in $OUTPUT_DIR"
echo ""

# Calculate size
echo "Calculating total size..."
total_size=$(du -sh "$OUTPUT_DIR" | cut -f1)
echo "Total size: $total_size"
echo ""

# Create archive
archive_name="depth_frames_PregnancyCravingsGoneWrongNew_$(date +%Y%m%d_%H%M%S).tar.gz"
echo "Creating archive: $archive_name"
echo "This may take a few minutes for large frame sets..."
echo ""

cd depth
tar -czf "../$archive_name" "PregnancyCravingsGoneWrongNew/" \
    --checkpoint=1000 \
    --checkpoint-action=echo='%T: %u files archived'

if [ $? -eq 0 ]; then
    cd ..
    archive_size=$(du -sh "$archive_name" | cut -f1)

    echo ""
    echo "=========================================="
    echo "✓ SUCCESS! Archive created"
    echo "=========================================="
    echo ""
    echo "Archive: $archive_name"
    echo "Size: $archive_size"
    echo "Frames: $frame_count"
    echo ""
    echo "Download options:"
    echo ""
    echo "1. RunPod Web Interface:"
    echo "   - Go to your pod's file browser"
    echo "   - Navigate to: /workspace/AUTO_2D_TO_3D_VIDEO_RUNPOD/"
    echo "   - Right-click on $archive_name and download"
    echo ""
    echo "2. SCP (from your local machine):"
    echo "   scp root@YOUR_RUNPOD_IP:~/AUTO_2D_TO_3D_VIDEO_RUNPOD/$archive_name ."
    echo ""
    echo "3. rsync (from your local machine):"
    echo "   rsync -avz --progress root@YOUR_RUNPOD_IP:~/AUTO_2D_TO_3D_VIDEO_RUNPOD/$archive_name ."
    echo ""
    echo "4. HTTP server (serve from pod):"
    echo "   python3 -m http.server 8000"
    echo "   Then access: http://YOUR_RUNPOD_IP:8000/"
    echo ""
    echo "After downloading, extract on your local machine:"
    echo "   tar -xzf $archive_name"
    echo ""
    echo "Then encode locally:"
    echo "   cd PregnancyCravingsGoneWrongNew"
    echo "   ffmpeg -framerate 23.98 -pattern_type glob -i '*.png' \\"
    echo "     -c:v libx264 -crf 18 -pix_fmt yuv420p depth_video.mp4"
    echo ""
else
    echo "✗ Failed to create archive"
    exit 1
fi
