"""
Debug intrinsics scaling issues when DA3 resizes images.
"""

import cv2
import numpy as np
from pathlib import Path
import sys

if len(sys.argv) < 2:
    print("Usage: python debug_intrinsics.py <scene_dir>")
    sys.exit(1)

scene_dir = Path(sys.argv[1])
left_dir = scene_dir / "left"
calib_file = "stereo_calib.npz"

# Load calibration
calib = np.load(calib_file)
K_orig = calib["K1"].astype(np.float32)

print(f"Original calibration K1:\n{K_orig}\n")

# Load first image to check dimensions
img_paths = sorted(left_dir.glob("*.jpg")) + sorted(left_dir.glob("*.png"))
if not img_paths:
    print("No images found")
    sys.exit(1)

img = cv2.imread(str(img_paths[0]))
h_orig, w_orig = img.shape[:2]
print(f"Original image size: {w_orig} x {h_orig}")

# DA3 processes at resolution 504 (upper bound resize)
# Let's check what the actual processed size would be
process_res = 504
max_dim = max(h_orig, w_orig)
scale = process_res / max_dim
h_proc = int(h_orig * scale)
w_proc = int(w_orig * scale)
print(f"DA3 processed size: {w_proc} x {h_proc} (scale factor: {scale:.4f})")

# Scale intrinsics accordingly
K_scaled = K_orig.copy()
K_scaled[0, 0] *= scale  # fx
K_scaled[1, 1] *= scale  # fy
K_scaled[0, 2] *= scale  # cx
K_scaled[1, 2] *= scale  # cy

print(f"\nScaled K for processed resolution:\n{K_scaled}")
print(f"\nDifference in focal lengths:")
print(f"  fx: {K_scaled[0,0]:.2f} vs {K_orig[0,0]:.2f} ({100*(scale-1):.1f}%)")
print(f"  fy: {K_scaled[1,1]:.2f} vs {K_orig[1,1]:.2f} ({100*(scale-1):.1f}%)")
print(f"  cx: {K_scaled[0,2]:.2f} vs {K_orig[0,2]:.2f}")
print(f"  cy: {K_scaled[1,2]:.2f} vs {K_orig[1,2]:.2f}")

# After inference, DA3 resizes depth back to original resolution
# But the points are backprojected using ORIGINAL resolution intrinsics
# This mismatch could cause offsets!
print(f"\n[!] POTENTIAL ISSUE:")
print(f"  If DA3 processes at {w_proc}x{h_proc} but we backproject at {w_orig}x{h_orig}")
print(f"  using original K, there will be geometric misalignment.")
