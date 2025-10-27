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

# Check for GPU
print_info "Checking for GPU availability..."
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
    print_success "GPU detected"
else
    print_error "No GPU detected! This script requires a CUDA-capable GPU."
    exit 1
fi

# Check for Python and PyTorch
print_info "Checking Python and PyTorch..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_info "Python version: $PYTHON_VERSION"

    # Check if PyTorch is installed
    if python3 -c "import torch" 2>/dev/null; then
        PYTORCH_VERSION=$(python3 -c "import torch; print(torch.__version__)")
        print_info "PyTorch version: $PYTORCH_VERSION"

        # Check CUDA availability
        if python3 -c "import torch; exit(0 if torch.cuda.is_available() else 1)" 2>/dev/null; then
            CUDA_VERSION=$(python3 -c "import torch; print(torch.version.cuda)")
            print_success "CUDA available (version: $CUDA_VERSION)"
        else
            print_error "PyTorch is installed but CUDA is not available!"
            print_info "Please use a RunPod template with PyTorch + CUDA support"
            exit 1
        fi
    else
        print_info "PyTorch not found. Will be installed with dependencies."
    fi
else
    print_error "Python 3 not found!"
    exit 1
fi

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
print_info "This may take a few minutes..."

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
print_info "Python version: $PYTHON_VERSION"

# Install common dependencies explicitly to avoid issues
print_info "Installing core dependencies..."
# Don't upgrade wheel if it's from debian package - causes issues
pip3 install --upgrade pip setuptools 2>&1 | grep -v "uninstall-no-record-file" || true

# IMPORTANT: Video-Depth-Anything's requirements.txt has old versions that don't work with Python 3.12
# We install compatible versions manually instead
print_info "Installing Python 3.12-compatible dependencies..."

# Install PyTorch and torchvision (should already be installed from RunPod template)
if ! python3 -c "import torch" 2>/dev/null; then
    print_info "PyTorch not found, installing..."
    pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu121
fi

# Install compatible versions for Python 3.12
print_info "Installing compatible package versions..."
pip3 install \
    "numpy>=1.26.0" \
    "opencv-python>=4.8.0" \
    "pillow>=10.0.0" \
    "tqdm>=4.65.0" \
    "einops>=0.7.0" \
    "huggingface-hub>=0.19.0"

print_success "Core dependencies installed with Python 3.12-compatible versions"

# Install additional common dependencies that might be missing
# NOTE: xformers is NOT installed - it causes flash-attention CUDA compatibility errors on some GPUs
print_info "Installing additional dependencies..."
pip3 install opencv-python-headless tqdm pyyaml notebook ipywidgets einops easydict matplotlib imageio imageio-ffmpeg

# Verify critical imports
print_info "Verifying Python dependencies..."
python3 -c "import torch; print('✓ PyTorch:', torch.__version__)" || (print_error "PyTorch import failed" && exit 1)
python3 -c "import cv2; print('✓ OpenCV:', cv2.__version__)" || (print_error "OpenCV import failed" && exit 1)
python3 -c "import numpy; print('✓ NumPy:', numpy.__version__)" || (print_error "NumPy import failed" && exit 1)
python3 -c "import tqdm; print('✓ tqdm: OK')" || (print_error "tqdm import failed" && exit 1)
python3 -c "import einops; print('✓ einops: OK')" || (print_error "einops import failed" && exit 1)
python3 -c "import yaml; print('✓ PyYAML: OK')" || (print_error "PyYAML import failed" && exit 1)
# xformers verification removed - we don't install it anymore due to CUDA compatibility issues

print_success "All Python dependencies installed and verified"

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
# NOTE: Metric models have the prefix "metric_" not suffix "_metric"
print_info "Checking for metric depth models (optional)..."
print_info "Note: Metric models may not be available on Hugging Face"
print_info "If you don't need metric depth, set metric: false in config.yaml"

# Try to download with correct naming: metric_video_depth_anything_*.pth
if [ ! -f "metric_video_depth_anything_vits.pth" ]; then
    print_info "Attempting to download metric depth model (Small)..."
    wget -q --show-progress \
        https://huggingface.co/depth-anything/Video-Depth-Anything-Small/resolve/main/metric_video_depth_anything_vits.pth \
        2>/dev/null || print_info "Metric Small model not available (this is normal)"
fi

if [ ! -f "metric_video_depth_anything_vitl.pth" ]; then
    print_info "Attempting to download metric depth model (Large)..."
    wget -q --show-progress \
        https://huggingface.co/depth-anything/Video-Depth-Anything-Large/resolve/main/metric_video_depth_anything_vitl.pth \
        2>/dev/null || print_info "Metric Large model not available (this is normal)"
fi

print_info "Standard (relative depth) models are ready to use"
print_info "If metric models failed to download, use metric: false in config.yaml"

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

# Show system information
print_info "System Information:"
echo ""
if command -v nvidia-smi &> /dev/null; then
    GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -n1)
    GPU_MEMORY=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -n1)
    echo "GPU: $GPU_NAME"
    echo "VRAM: ${GPU_MEMORY} MB (~$((GPU_MEMORY/1024)) GB)"
    echo ""

    # Give recommendations based on VRAM
    if [ "$GPU_MEMORY" -lt 10000 ]; then
        print_info "Recommendation: Use Small model (encoder: vits) in config.yaml"
        print_info "Your GPU has limited VRAM. Stick to 1080p videos."
    elif [ "$GPU_MEMORY" -lt 16000 ]; then
        print_info "Recommendation: Use Small model for best performance"
        print_info "Large model may work for 1080p but could run out of memory on 4K"
    else
        print_success "Your GPU can handle both Small and Large models!"
        print_info "Large model (encoder: vitl) is set by default in config.yaml"
    fi
fi

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
echo "Documentation:"
echo "  README.md               - Full documentation"
echo "  QUICKSTART.md           - Quick start guide"
echo "  HARDWARE_REQUIREMENTS.md - GPU, PyTorch, and storage guide"
echo ""
print_info "For StereoPhotoMaker setup, place the application in the 'stereophotomaker' folder"
echo "========================================"
