#!/bin/bash

# Model Download Script for Video-Depth-Anything
# Downloads the required model checkpoint files

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================"
echo "Video-Depth-Anything Model Downloader"
echo "========================================"
echo ""

# Check if Video-Depth-Anything exists
if [ ! -d "Video-Depth-Anything" ]; then
    echo -e "${RED}[ERROR]${NC} Video-Depth-Anything directory not found!"
    echo "Please run ./setup_runpod.sh first"
    exit 1
fi

# Create checkpoints directory
mkdir -p Video-Depth-Anything/checkpoints
cd Video-Depth-Anything/checkpoints

echo -e "${BLUE}[INFO]${NC} Downloading model checkpoints..."
echo -e "${BLUE}[INFO]${NC} This may take 5-10 minutes depending on your connection"
echo ""

# Function to download and verify
download_model() {
    local MODEL_NAME=$1
    local MODEL_URL=$2
    local MODEL_SIZE=$3

    if [ -f "${MODEL_NAME}" ]; then
        echo -e "${GREEN}[FOUND]${NC} ${MODEL_NAME} already exists"
        ls -lh "${MODEL_NAME}"
        return 0
    fi

    echo -e "${YELLOW}[DOWNLOADING]${NC} ${MODEL_NAME} (~${MODEL_SIZE})..."
    echo "URL: ${MODEL_URL}"

    if wget --show-progress -O "${MODEL_NAME}" "${MODEL_URL}"; then
        echo -e "${GREEN}[SUCCESS]${NC} Downloaded ${MODEL_NAME}"
        ls -lh "${MODEL_NAME}"
        echo ""
    else
        echo -e "${RED}[FAILED]${NC} Could not download ${MODEL_NAME}"
        echo "Please try downloading manually from:"
        echo "${MODEL_URL}"
        return 1
    fi
}

# Download Small Model
echo "========================================"
echo "1. Small Model (vits - 28.4M params)"
echo "========================================"
download_model \
    "video_depth_anything_vits.pth" \
    "https://huggingface.co/depth-anything/Video-Depth-Anything-Small/resolve/main/video_depth_anything_vits.pth" \
    "100 MB"

# Download Large Model
echo "========================================"
echo "2. Large Model (vitl - 335M params)"
echo "========================================"
download_model \
    "video_depth_anything_vitl.pth" \
    "https://huggingface.co/depth-anything/Video-Depth-Anything-Large/resolve/main/video_depth_anything_vitl.pth" \
    "700 MB"

echo ""
echo "========================================"
echo "Download Summary"
echo "========================================"
echo ""
echo "Models in checkpoints directory:"
ls -lh *.pth 2>/dev/null || echo "No .pth files found!"
echo ""

# Verify required models exist
MISSING=0

if [ ! -f "video_depth_anything_vits.pth" ]; then
    echo -e "${RED}[MISSING]${NC} video_depth_anything_vits.pth"
    MISSING=1
else
    echo -e "${GREEN}[OK]${NC} video_depth_anything_vits.pth"
fi

if [ ! -f "video_depth_anything_vitl.pth" ]; then
    echo -e "${RED}[MISSING]${NC} video_depth_anything_vitl.pth"
    MISSING=1
else
    echo -e "${GREEN}[OK]${NC} video_depth_anything_vitl.pth"
fi

echo ""

if [ $MISSING -eq 1 ]; then
    echo -e "${RED}[ERROR]${NC} Some models are missing!"
    echo ""
    echo "Manual download instructions:"
    echo "1. Go to: https://huggingface.co/depth-anything/Video-Depth-Anything-Small"
    echo "2. Download: video_depth_anything_vits.pth"
    echo "3. Go to: https://huggingface.co/depth-anything/Video-Depth-Anything-Large"
    echo "4. Download: video_depth_anything_vitl.pth"
    echo "5. Place files in: Video-Depth-Anything/checkpoints/"
    echo ""
    exit 1
else
    echo -e "${GREEN}[SUCCESS]${NC} All required models downloaded!"
    echo ""
    echo "You can now run: ./process_video.py"
    echo ""
fi

cd ../..
