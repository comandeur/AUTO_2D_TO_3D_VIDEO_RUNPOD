#!/bin/bash

# Safe Video Download from URL
# Downloads video from URL with verification

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

if [ $# -eq 0 ]; then
    echo "Usage: $0 <video_url> [output_filename]"
    echo ""
    echo "Examples:"
    echo "  $0 https://example.com/video.mp4"
    echo "  $0 https://example.com/video.mp4 my_video.mp4"
    echo "  $0 https://transfer.sh/xxxxx/video.mp4"
    exit 1
fi

URL=$1
OUTPUT_FILE=${2:-"$(basename "$URL")"}

# Create in directory if it doesn't exist
mkdir -p in

cd in

echo "========================================"
echo "Safe Video Download"
echo "========================================"
echo ""
echo "URL: $URL"
echo "Output: $OUTPUT_FILE"
echo ""

# Download with resume support
echo -e "${BLUE}[DOWNLOADING]${NC} Starting download..."
echo ""

if wget -c --show-progress -O "$OUTPUT_FILE" "$URL"; then
    echo ""
    echo -e "${GREEN}[SUCCESS]${NC} Download completed!"
else
    echo ""
    echo -e "${RED}[FAILED]${NC} Download failed!"
    echo "The file may be partially downloaded. Run the script again to resume."
    exit 1
fi

# Show file info
echo ""
echo "File size: $(du -h "$OUTPUT_FILE" | cut -f1)"
echo ""

# Validate the video
echo "========================================"
echo "Validating Video File"
echo "========================================"
echo ""

if ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$OUTPUT_FILE" > /dev/null 2>&1; then
    DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$OUTPUT_FILE")
    echo -e "${GREEN}[VALID]${NC} Video file is OK"
    echo "Duration: ${DURATION}s"
    echo ""
    echo "You can now run: ./process_video.py"
else
    echo -e "${RED}[INVALID]${NC} Video file appears to be corrupted!"
    echo ""
    echo "Try downloading again or check the source URL."
    exit 1
fi

cd ..
