# Safe Video Upload Guide for RunPod

This guide helps you upload large video files to RunPod without corruption.

---

## Problem: Files Getting Corrupted During Upload

When uploading large videos (especially >100MB), files can get corrupted due to:
- Network interruptions
- Incomplete transfers
- Browser timeouts
- Connection drops

**Error you'll see:**
```
[mov,mp4,m4a,3gp,3g2,mj2] moov atom not found
ZeroDivisionError: float division by zero
```

---

## Solution 1: Use rsync (Recommended for Large Files)

**From your local PC:**

```bash
# Install rsync if you don't have it
# Windows: Install Git Bash or WSL
# Mac/Linux: Already installed

# Upload with rsync (resumes if interrupted!)
rsync -avz --progress \
  "/path/to/your/video.mp4" \
  root@your-runpod-ip:/workspace/AUTO_2D_TO_3D_VIDEO_RUNPOD/in/

# With SSH key:
rsync -avz --progress -e "ssh -i ~/.ssh/runpod_key" \
  "/path/to/your/video.mp4" \
  root@your-runpod-ip:/workspace/AUTO_2D_TO_3D_VIDEO_RUNPOD/in/
```

**Advantages:**
- ✅ Resumes interrupted transfers
- ✅ Verifies file integrity
- ✅ Shows progress
- ✅ Handles large files (>1GB) easily

---

## Solution 2: Upload with MD5 Verification

### On Your Local PC:

```bash
# 1. Calculate checksum of your video
md5sum "video.mp4" > video.mp4.md5
# Mac users: md5 -r "video.mp4" > video.mp4.md5

# 2. Upload both files
scp video.mp4 video.mp4.md5 root@runpod-ip:/workspace/AUTO_2D_TO_3D_VIDEO_RUNPOD/in/
```

### On RunPod:

```bash
# Verify the upload
cd /workspace/AUTO_2D_TO_3D_VIDEO_RUNPOD/in
md5sum -c video.mp4.md5

# Should show: video.mp4: OK
```

---

## Solution 3: Split Large Files (For Unstable Connections)

### On Your Local PC:

```bash
# Split video into 100MB chunks
split -b 100M "large_video.mp4" "video_part_"

# Upload each chunk
scp video_part_* root@runpod-ip:/workspace/AUTO_2D_TO_3D_VIDEO_RUNPOD/in/
```

### On RunPod:

```bash
# Rejoin the parts
cd /workspace/AUTO_2D_TO_3D_VIDEO_RUNPOD/in
cat video_part_* > large_video.mp4

# Remove parts
rm video_part_*

# Verify it's valid
./validate_videos.sh
```

---

## Solution 4: Use RunPod's Web Interface (For Smaller Files)

**Best for files < 500 MB**

1. Open RunPod web terminal
2. Click the folder icon 📁
3. Navigate to `/workspace/AUTO_2D_TO_3D_VIDEO_RUNPOD/in/`
4. Click "Upload" button
5. Select your video
6. **IMPORTANT:** Wait for "Upload complete" message
7. Verify: `./validate_videos.sh`

**Tips:**
- Don't close browser during upload
- Use wired connection, not WiFi
- Upload one file at a time for large files

---

## Solution 5: Use Cloud Storage as Intermediary

### Via Dropbox/Google Drive:

**On Your PC:**
1. Upload to Dropbox/Google Drive
2. Get sharing link

**On RunPod:**
```bash
cd /workspace/AUTO_2D_TO_3D_VIDEO_RUNPOD/in

# From Dropbox
wget -O video.mp4 "https://www.dropbox.com/YOUR_SHARE_LINK?dl=1"

# From Google Drive (for small files)
wget --no-check-certificate -O video.mp4 "https://drive.google.com/uc?export=download&id=FILE_ID"

# For large Google Drive files, use gdown
pip install gdown
gdown "https://drive.google.com/uc?id=FILE_ID" -O video.mp4
```

### Via Transfer.sh (Temporary):

**On Your PC:**
```bash
# Upload (keeps for 14 days)
curl --upload-file video.mp4 https://transfer.sh/video.mp4
# Returns: https://transfer.sh/xxxxx/video.mp4
```

**On RunPod:**
```bash
cd /workspace/AUTO_2D_TO_3D_VIDEO_RUNPOD/in
wget https://transfer.sh/xxxxx/video.mp4
```

---

## Solution 6: Direct URL Download (If Video is Online)

If your video is already online:

```bash
cd /workspace/AUTO_2D_TO_3D_VIDEO_RUNPOD/in

# Simple download
wget "https://your-video-url.com/video.mp4"

# With resume support (if interrupted)
wget -c "https://your-video-url.com/video.mp4"

# Show progress
wget --show-progress "https://your-video-url.com/video.mp4"
```

---

## Recommended Upload Method by File Size

| File Size | Best Method | Why |
|-----------|-------------|-----|
| < 100 MB | RunPod Web UI | Fast and simple |
| 100MB - 500MB | SCP or Web UI | Both work well |
| 500MB - 2GB | **rsync** | Resumes if interrupted |
| > 2GB | **rsync** or Cloud Storage | Most reliable |
| > 5GB | **Cloud Storage** → wget | Handles network issues |

---

## Verification After Upload

**ALWAYS run this after uploading:**

```bash
./validate_videos.sh
```

This will tell you if the upload was successful or if the file got corrupted.

If validation fails:
- ✗ File is corrupted - re-upload needed
- ✓ File is valid - ready to process!

---

## Troubleshooting Upload Issues

### "Connection timed out"
```bash
# Use rsync with longer timeout
rsync -avz --timeout=300 --progress video.mp4 root@runpod:/path/
```

### "Permission denied"
```bash
# Make sure you have the right SSH key
ssh -i ~/.ssh/runpod_key root@runpod-ip

# Or use RunPod's web terminal for uploads
```

### "Disk quota exceeded"
```bash
# Check available space on RunPod
df -h

# Clean up old files
rm -rf depth/*  # Remove old output
```

### Upload keeps failing
1. Use **rsync** (it resumes)
2. Or upload to Dropbox first, then wget on RunPod
3. Check your internet connection stability

---

## Example: Complete Safe Upload Workflow

### On Your PC:

```bash
# 1. Calculate checksum
md5sum "MyVideo.mp4" > MyVideo.mp4.md5

# 2. Upload with rsync (resumes if interrupted)
rsync -avz --progress \
  "MyVideo.mp4" "MyVideo.mp4.md5" \
  root@runpod-ip:/workspace/AUTO_2D_TO_3D_VIDEO_RUNPOD/in/
```

### On RunPod:

```bash
cd /workspace/AUTO_2D_TO_3D_VIDEO_RUNPOD

# 3. Verify upload integrity
cd in
md5sum -c MyVideo.mp4.md5
# Should show: MyVideo.mp4: OK

# 4. Validate video is not corrupted
cd ..
./validate_videos.sh

# 5. If valid, process it!
./process_video.py
```

---

## Quick Fix for Already Uploaded Corrupted Videos

If you already uploaded and it's corrupted:

```bash
# Don't re-upload! Try to repair first:
ffmpeg -i corrupted.mp4 -c copy repaired.mp4

# Or full re-encode:
ffmpeg -i corrupted.mp4 -c:v libx264 -c:a aac fixed.mp4
```

If repair fails → delete and re-upload using the methods above.

---

## Summary

**Best Practice Workflow:**

1. **Upload:** Use `rsync` for reliability
2. **Verify:** Run `./validate_videos.sh`
3. **Process:** Run `./process_video.py`

This prevents corruption and wasted GPU time!

---

## Need Help?

**Check if file is corrupted:**
```bash
./validate_videos.sh
```

**Most reliable upload:**
```bash
rsync -avz --progress video.mp4 root@runpod:/workspace/AUTO_2D_TO_3D_VIDEO_RUNPOD/in/
```

**If all else fails:**
Upload to Dropbox → wget on RunPod
