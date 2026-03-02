# Stereo Camera Calibration & Rectification for Quest 3

This project provides a complete stereo camera calibration and
rectification pipeline using OpenCV.

The goal is to: - Calibrate two cameras as a stereo rig - Rectify images
to eliminate vertical disparity - Prepare left/right frames for
stereoscopic rendering in Meta Quest 3 (PC → Quest via Link/AirLink)

------------------------------------------------------------------------

## Project Overview

This repository performs:

1.  Chessboard-based stereo calibration
2.  Intrinsic and extrinsic parameter estimation
3.  Stereo rectification
4.  Side-by-side rectified image verification
5.  Preparation for VR stereo rendering

After rectification, the left and right images can be directly mapped to
VR eyes for depth perception.

------------------------------------------------------------------------

## Repository Structure

    .
    ├── calib/
    │   ├── left/
    │   └── right/
    ├── debug/
    ├── stereo_calib.npz
    ├── main.py
    ├── new.py
    └── README.md

-   `calib/left/` → raw left calibration images\
-   `calib/right/` → raw right calibration images\
-   `debug/` → images with detected corners drawn\
-   `stereo_calib.npz` → saved calibration parameters\
-   `main.py` → stereo calibration script\
-   `new.py` → rectification verification

------------------------------------------------------------------------

## Calibration Pattern

This project assumes a **12 × 8 squares chessboard**.

OpenCV requires **inner corners**, not squares.

If your board has:

12 × 8 squares

Then you must use:

(11, 7) inner corners

Set in code:

``` python
chessboard_size = (11, 7)
```

------------------------------------------------------------------------

## Installation

Install dependencies:

``` bash
pip install opencv-python numpy
```

Recommended OpenCV version: 4.x

------------------------------------------------------------------------

## Step 1 -- Capture Calibration Images

Requirements:

-   15--30 stereo image pairs
-   Same resolution for both cameras
-   Chessboard fully visible
-   Different angles, positions, distances
-   Good lighting
-   No motion blur

Folder structure:

    calib/
     ├── left/
     └── right/

------------------------------------------------------------------------

## Step 2 -- Run Stereo Calibration

``` bash
python main.py
```

Expected output:

-   Valid stereo pairs: 15+
-   Left reprojection error: 0.2--1.0
-   Right reprojection error: 0.2--1.0
-   Stereo calibration RMS error: 0.3--1.5

This generates:

    stereo_calib.npz

------------------------------------------------------------------------

## Step 3 -- Verify Rectification

``` bash
python new.py
```

This will: - Load one left/right image - Apply rectification - Show both
images side-by-side - Draw horizontal guide lines

Correct rectification means corresponding features align horizontally.

------------------------------------------------------------------------

## Baseline Verification

To compute stereo baseline:

``` python
import numpy as np
baseline = np.linalg.norm(T)
print(baseline)
```

This should match your physical camera spacing (e.g., \~0.06 meters).

------------------------------------------------------------------------

## Next Step -- Quest 3 Integration

Once rectified images are verified:

-   Send `rect_l` → Left eye texture
-   Send `rect_r` → Right eye texture
-   Add convergence adjustment in Unity

This enables true binocular stereoscopic depth in VR.

------------------------------------------------------------------------

## Common Issues

**Valid stereo pairs = 0** - Wrong chessboard size - Chessboard
partially visible - Poor lighting - Images not loading correctly

**Corners not detected** Use:

``` python
cv2.findChessboardCornersSB()
```

**Eye strain in VR** - No rectification - Vertical disparity -
Unsynchronized cameras
