#!/bin/bash

# Quick fix script for missing Python dependencies
# Run this if you get "ModuleNotFoundError" errors

echo "=========================================="
echo "Fixing Python Dependencies"
echo "=========================================="

echo "[INFO] Upgrading pip..."
pip3 install --upgrade pip setuptools wheel

echo ""
echo "[INFO] Installing common missing dependencies..."
pip3 install opencv-python opencv-python-headless tqdm pyyaml notebook ipywidgets einops easydict matplotlib imageio imageio-ffmpeg xformers

echo ""
echo "[INFO] Verifying installations..."
python3 -c "import cv2; print('✓ OpenCV (cv2):', cv2.__version__)" || echo "✗ OpenCV failed"
python3 -c "import tqdm; print('✓ tqdm: OK')" || echo "✗ tqdm failed"
python3 -c "import yaml; print('✓ PyYAML: OK')" || echo "✗ PyYAML failed"
python3 -c "import einops; print('✓ einops: OK')" || echo "✗ einops failed"
python3 -c "import xformers; print('✓ xformers:', xformers.__version__)" || echo "✗ xformers failed"
python3 -c "import torch; print('✓ PyTorch:', torch.__version__)" || echo "✗ PyTorch failed (install from template)"
python3 -c "import numpy; print('✓ NumPy:', numpy.__version__)" || echo "✗ NumPy failed"

echo ""
echo "=========================================="
echo "Dependencies check complete!"
echo "=========================================="
echo ""
echo "If any checks failed, try:"
echo "1. Ensure you're using a PyTorch RunPod template"
echo "2. Run: pip3 install -r requirements.txt"
echo "3. Check TROUBLESHOOTING.md for more help"
