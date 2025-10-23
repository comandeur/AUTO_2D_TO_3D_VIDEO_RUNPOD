#!/bin/bash

# RunPod Setup Script for 2D to 3D Video Conversion
# This script sets up the environment on a RunPod instance

set -e

echo "========================================"
echo "RunPod 2D to 3D Video Conversion Setup"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

# Check if we're in the correct directory
if [ ! -f "config.yaml" ]; then
    print_error "config.yaml not found. Please run this script from the repository root."
    exit 1
fi

print_info "Starting setup..."

# Update system packages
print_info "Updating system packages..."
apt-get update -qq

# Install required system packages
print_info "Installing system dependencies..."
apt-get install -y -qq \
    git \
    wget \
    ffmpeg \
    python3-pip \
    python3-venv \
    || print_error "Failed to install system packages"

print_success "System dependencies installed"

# Clone Video-Depth-Anything if not already present
if [ ! -d "Video-Depth-Anything" ]; then
    print_info "Cloning Video-Depth-Anything repository..."
    git clone https://github.com/DepthAnything/Video-Depth-Anything.git
    print_success "Video-Depth-Anything repository cloned"
else
    print_info "Video-Depth-Anything already exists, skipping clone"
fi

# Set up Video-Depth-Anything
cd Video-Depth-Anything

print_info "Installing Python dependencies for Video-Depth-Anything..."
pip3 install -q -r requirements.txt || print_error "Failed to install Python requirements"
print_success "Python dependencies installed"

# Create checkpoints directory
mkdir -p checkpoints

# Download model checkpoints
print_info "Downloading model checkpoints..."
print_info "This may take a while depending on your connection speed..."

# Check which models to download based on config
cd checkpoints

# Download Small model (always useful to have)
if [ ! -f "video_depth_anything_vits.pth" ]; then
    print_info "Downloading Video-Depth-Anything-Small model..."
    wget -q --show-progress \
        https://huggingface.co/depth-anything/Video-Depth-Anything-Small/resolve/main/video_depth_anything_vits.pth \
        || print_error "Failed to download Small model"
    print_success "Small model downloaded"
else
    print_info "Small model already exists"
fi

# Download Large model
if [ ! -f "video_depth_anything_vitl.pth" ]; then
    print_info "Downloading Video-Depth-Anything-Large model..."
    wget -q --show-progress \
        https://huggingface.co/depth-anything/Video-Depth-Anything-Large/resolve/main/video_depth_anything_vitl.pth \
        || print_error "Failed to download Large model"
    print_success "Large model downloaded"
else
    print_info "Large model already exists"
fi

# Download metric depth models if needed
print_info "Checking for metric depth models..."

if [ ! -f "video_depth_anything_metric_vits.pth" ]; then
    print_info "Downloading metric depth model (Small)..."
    wget -q --show-progress \
        https://huggingface.co/depth-anything/Video-Depth-Anything-Small/resolve/main/video_depth_anything_metric_vits.pth \
        || print_info "Metric Small model not available or failed to download"
fi

if [ ! -f "video_depth_anything_metric_vitl.pth" ]; then
    print_info "Downloading metric depth model (Large)..."
    wget -q --show-progress \
        https://huggingface.co/depth-anything/Video-Depth-Anything-Large/resolve/main/video_depth_anything_metric_vitl.pth \
        || print_info "Metric Large model not available or failed to download"
fi

cd ../..

# Install additional Python dependencies for the main script
print_info "Installing additional Python dependencies..."
pip3 install -q pyyaml || print_error "Failed to install PyYAML"
print_success "Additional dependencies installed"

# Make scripts executable
chmod +x process_video.py
chmod +x setup_runpod.sh

# Create folder structure if not exists
mkdir -p in depth stereophotomaker

print_success "Folder structure created"

# Display setup completion
echo ""
echo "========================================"
print_success "Setup completed successfully!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Place your 2D videos in the 'in' folder"
echo "2. Adjust settings in 'config.yaml' if needed"
echo "3. Run: ./process_video.py"
echo ""
echo "Folder structure:"
echo "  in/              - Place input 2D videos here"
echo "  depth/           - Depth videos will be saved here"
echo "  stereophotomaker/- For StereoPhotoMaker (future use)"
echo "  Video-Depth-Anything/ - Depth estimation tool"
echo ""
echo "Configuration:"
echo "  config.yaml      - Adjust processing parameters here"
echo ""
print_info "For StereoPhotoMaker setup, place the application in the 'stereophotomaker' folder"
echo "========================================"
