#!/bin/bash

# Diagnostic script to check what caused OOM kill

echo "=========================================="
echo "OOM Kill Diagnostic"
echo "=========================================="
echo ""

echo "=== Current System Resources ==="
echo ""
echo "RAM Usage:"
free -h
echo ""
echo "Swap Status:"
swapon --show || echo "No swap configured"
echo ""
echo "Disk Space:"
df -h | grep -E "Filesystem|workspace|/$"
echo ""

echo "=== Check System Logs for OOM Kills ==="
echo ""
if command -v dmesg &> /dev/null; then
    echo "Recent OOM kills from dmesg:"
    dmesg | grep -i "killed process\|out of memory\|oom" | tail -20
    echo ""
else
    echo "dmesg not available"
fi

echo "=== Check Output Directory ==="
echo ""
if [ -d "depth/PregnancyCravingsGoneWrongNew" ]; then
    echo "Output directory exists:"
    ls -lh depth/PregnancyCravingsGoneWrongNew/
    echo ""

    # Check if frames were extracted
    frame_count=$(find depth/PregnancyCravingsGoneWrongNew -name "*.png" -o -name "*.jpg" 2>/dev/null | wc -l)
    echo "Total frames extracted: $frame_count"

    # Check if video was created
    if [ -f "depth/PregnancyCravingsGoneWrongNew/depth_video.mp4" ]; then
        echo "✓ Depth video was created!"
        ls -lh depth/PregnancyCravingsGoneWrongNew/depth_video.mp4
    else
        echo "✗ Final depth video NOT found"
        echo "Frames were processed but video encoding failed"
    fi
else
    echo "✗ Output directory not found"
fi

echo ""
echo "=== Recommendations ==="
echo ""
echo "If killed by OOM (Out Of Memory):"
echo "1. Your system may have run out of RAM during video encoding"
echo "2. RunPod instance might have insufficient RAM"
echo "3. Try solutions in fix_oom.sh"
echo ""
echo "Check if frames were saved:"
echo "  ls -lh depth/PregnancyCravingsGoneWrongNew/"
echo ""
echo "If frames exist but no video, manually encode:"
echo "  cd depth/PregnancyCravingsGoneWrongNew"
echo "  ffmpeg -framerate 23.98 -i %05d.png -c:v libx264 -pix_fmt yuv420p depth_video.mp4"
