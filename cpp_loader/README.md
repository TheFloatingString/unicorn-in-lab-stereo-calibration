# stereo_rectify

C++ implementation of stereo rectification using OpenCV. Loads calibration maps from `stereo_calib.npz`, remaps left/right images, draws horizontal guide lines, and displays them side-by-side.

## Prerequisites

- [CMake](https://cmake.org/) 3.16+
- [Visual Studio Build Tools 2022](https://visualstudio.microsoft.com/downloads/)
- [vcpkg](https://github.com/microsoft/vcpkg) bootstrapped at `C:/vcpkg`

If vcpkg is not yet set up:
```powershell
git clone https://github.com/microsoft/vcpkg.git C:/vcpkg
C:/vcpkg/bootstrap-vcpkg.bat
```

## Build

### 1. Install dependencies (~15–30 min, one-time)
```powershell
C:\vcpkg\vcpkg.exe install --triplet x64-windows
```

### 2. Configure CMake (~2–5 min, downloads cnpy via FetchContent)
```powershell
cd C:\Users\laure\Projects\unicorn-repo-1\stereo_calibration-main\cpp_loader
cmake -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_TOOLCHAIN_FILE=C:/vcpkg/scripts/buildsystems/vcpkg.cmake
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
