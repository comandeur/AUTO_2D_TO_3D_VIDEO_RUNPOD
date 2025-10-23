#!/bin/bash

# Video File Validation Script
# Checks if video files are valid before processing

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================"
echo "Video File Validation"
echo "========================================"
echo ""

if [ ! -d "in" ]; then
    echo -e "${RED}[ERROR]${NC} 'in' folder not found!"
    exit 1
fi

echo "Checking video files in 'in/' folder..."
echo ""

VALID_COUNT=0
INVALID_COUNT=0
TOTAL_COUNT=0

for video in in/*.{mp4,avi,mov,mkv,webm,flv} in/*.{MP4,AVI,MOV,MKV,WEBM,FLV}; do
    # Skip if glob didn't match any files
    [ -e "$video" ] || continue

    TOTAL_COUNT=$((TOTAL_COUNT + 1))

    echo "----------------------------------------"
    echo "File: $(basename "$video")"
    echo "----------------------------------------"

    # Check if file exists and is not empty
    if [ ! -s "$video" ]; then
        echo -e "${RED}[INVALID]${NC} File is empty or doesn't exist"
        INVALID_COUNT=$((INVALID_COUNT + 1))
        continue
    fi

    # Check file size
    SIZE=$(stat -f%z "$video" 2>/dev/null || stat -c%s "$video" 2>/dev/null)
    SIZE_MB=$((SIZE / 1024 / 1024))
    echo "Size: ${SIZE_MB} MB"

    # Validate with ffprobe
    if ffprobe -v error -show_entries format=duration,bit_rate -show_entries stream=codec_name,width,height,r_frame_rate -of json "$video" > /tmp/video_info.json 2>&1; then
        # Extract info
        DURATION=$(jq -r '.format.duration // "unknown"' /tmp/video_info.json 2>/dev/null || echo "unknown")
        WIDTH=$(jq -r '.streams[0].width // "unknown"' /tmp/video_info.json 2>/dev/null || echo "unknown")
        HEIGHT=$(jq -r '.streams[0].height // "unknown"' /tmp/video_info.json 2>/dev/null || echo "unknown")
        FPS=$(jq -r '.streams[0].r_frame_rate // "unknown"' /tmp/video_info.json 2>/dev/null || echo "unknown")
        CODEC=$(jq -r '.streams[0].codec_name // "unknown"' /tmp/video_info.json 2>/dev/null || echo "unknown")

        echo "Duration: ${DURATION}s"
        echo "Resolution: ${WIDTH}x${HEIGHT}"
        echo "FPS: ${FPS}"
        echo "Codec: ${CODEC}"

        # Check for critical issues
        if [ "$DURATION" = "unknown" ] || [ "$DURATION" = "null" ]; then
            echo -e "${RED}[INVALID]${NC} Cannot read video duration - file may be corrupted"
            echo "Try re-encoding: ffmpeg -i \"$video\" -c:v libx264 -c:a aac \"in/$(basename "${video%.*}")_fixed.mp4\""
            INVALID_COUNT=$((INVALID_COUNT + 1))
        elif [ "$FPS" = "unknown" ] || [ "$FPS" = "null" ] || [ "$FPS" = "0/0" ]; then
            echo -e "${YELLOW}[WARNING]${NC} Invalid FPS metadata"
            echo "Try re-encoding: ffmpeg -i \"$video\" -r 30 -c:v libx264 -c:a aac \"in/$(basename "${video%.*}")_fixed.mp4\""
            INVALID_COUNT=$((INVALID_COUNT + 1))
        else
            echo -e "${GREEN}[VALID]${NC} Video file is OK"
            VALID_COUNT=$((VALID_COUNT + 1))
        fi
    else
        echo -e "${RED}[INVALID]${NC} ffprobe failed - file is corrupted or not a valid video"

        # Show specific error
        ffprobe -v error "$video" 2>&1 | head -5

        echo ""
        echo "Common issues:"
        echo "1. 'moov atom not found' - Incomplete download, file is corrupted"
        echo "2. 'Invalid data found' - Not a valid video file or wrong format"
        echo ""
        echo "Solutions:"
        echo "- Re-download the video file"
        echo "- Try re-encoding: ffmpeg -i \"$video\" -c:v libx264 -c:a aac \"in/$(basename "${video%.*}")_fixed.mp4\""
        echo "- Verify the file is not empty: ls -lh \"$video\""

        INVALID_COUNT=$((INVALID_COUNT + 1))
    fi

    echo ""
done

# Summary
echo "========================================"
echo "Validation Summary"
echo "========================================"
echo "Total videos: $TOTAL_COUNT"
echo -e "${GREEN}Valid: $VALID_COUNT${NC}"
echo -e "${RED}Invalid: $INVALID_COUNT${NC}"
echo ""

if [ $INVALID_COUNT -gt 0 ]; then
    echo -e "${YELLOW}[WARNING]${NC} Some videos are invalid!"
    echo "Please fix the invalid videos before running ./process_video.py"
    echo ""
    echo "Quick fix for corrupted videos:"
    echo "  ffmpeg -i \"corrupted.mp4\" -c:v libx264 -c:a aac \"fixed.mp4\""
    exit 1
else
    echo -e "${GREEN}[SUCCESS]${NC} All videos are valid!"
    echo "You can now run: ./process_video.py"
    exit 0
fi
