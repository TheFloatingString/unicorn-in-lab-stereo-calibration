# stereo_rectify

C++ implementation of stereo rectification using OpenCV. Loads calibration maps from `stereo_calib.npz`, remaps left/right images, draws horizontal guide lines, and displays them side-by-side.

## Prerequisites

- [CMake](https://cmake.org/) 3.16+
- [Visual Studio Build Tools 2022](https://visualstudio.microsoft.com/downloads/)
- OpenCV 4.13 (bundled as `opencv-4.13.0-windows.exe` in this folder — includes zlib, no vcpkg needed)

## Build

### 1. Extract OpenCV (one-time)

Run the self-extracting installer and extract into this folder (`cpp_loader/`):

```powershell
cd C:\Users\laure\Projects\unicorn-repo-1\stereo_calibration-main\cpp_loader
.\opencv-4.13.0-windows.exe
```

When prompted for the extraction path, set it to:
```
C:\Users\laure\Projects\unicorn-repo-1\stereo_calibration-main\cpp_loader
```

This creates `cpp_loader/opencv/build/` which CMake detects automatically.

### 2. Configure CMake (~2–5 min, downloads cnpy via FetchContent)
```powershell
cd C:\Users\laure\Projects\unicorn-repo-1\stereo_calibration-main\cpp_loader
cmake -B build -DCMAKE_BUILD_TYPE=Release
```

If you extracted OpenCV to a different location, pass it explicitly:
```powershell
cmake -B build -DOpenCV_DIR="C:/path/to/opencv/build"
```

### 3. Build (~1 min)
```powershell
cmake --build build --config Release
```

## Run

Run from the parent directory so relative paths (`../calib/`, `../stereo_calib.npz`) resolve correctly:

```powershell
cd C:\Users\laure\Projects\unicorn-repo-1\stereo_calibration-main
cpp_loader\build\Release\stereo_rectify.exe
```

## Configuration

Edit the constants at the top of `main.cpp` to change input images or line spacing:

```cpp
const std::string LEFT_IMG   = "../calib/MAR_03_L.jpg";
const std::string RIGHT_IMG  = "../calib/MAR_03_R.jpg";
const std::string CALIB_FILE = "../stereo_calib.npz";
const int LINE_SPACING = 40; // pixels between horizontal guide lines
```
