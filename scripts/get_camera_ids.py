#!/usr/bin/env python3
"""
Scan all attached cameras and display their invariable fingerprints.
Works on Windows, Linux, and macOS.
"""

import cv2
import sys
import subprocess
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import json


def get_cameras_opencv() -> List[int]:
    """
    Detect available cameras using OpenCV.
    Returns list of camera indices.
    """
    available_cameras = []
    # Check up to 20 potential camera indices
    for i in range(20):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available_cameras.append(i)
            cap.release()
    return available_cameras


def get_all_usb_cameras_windows() -> Dict[int, Dict[str, str]]:
    """
    Query all USB cameras from Windows registry and WMI.
    Returns dict mapping device paths to camera info.
    """
    camera_devices = {}

    try:
        import winreg

        # Query Windows USB devices
        reg_path = r"SYSTEM\CurrentControlSet\Enum\USB"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
            for i in range(winreg.QueryInfoKey(key)[0]):
                vendor_id = winreg.EnumKey(key, i)
                try:
                    with winreg.OpenKey(key, vendor_id) as vendor_key:
                        for j in range(winreg.QueryInfoKey(vendor_key)[0]):
                            device_id = winreg.EnumKey(vendor_key, j)
                            try:
                                device_path = f"{vendor_id}\\{device_id}"
                                with winreg.OpenKey(vendor_key, device_id) as device_key:
                                    try:
                                        friendly_name = winreg.QueryValueEx(device_key, "FriendlyName")[0]
                                        device_desc = winreg.QueryValueEx(device_key, "DeviceDesc")[0]

                                        is_camera = (
                                            "camera" in friendly_name.lower() or
                                            "camera" in device_desc.lower() or
                                            "webcam" in friendly_name.lower() or
                                            "video" in device_desc.lower()
                                        )

                                        if is_camera:
                                            camera_devices[device_path] = {
                                                "friendly_name": friendly_name,
                                                "device_desc": device_desc,
                                                "device_path": device_path,
                                                "vendor_product_id": device_id,
                                            }
                                    except (OSError, FileNotFoundError):
                                        pass
                            except (OSError, FileNotFoundError):
                                pass
                except (OSError, FileNotFoundError):
                    pass

    except ImportError:
        pass
    except Exception as e:
        print(f"Error querying USB devices: {e}", file=sys.stderr)

    return camera_devices


def get_camera_properties_windows(camera_idx: int) -> Dict[str, str]:
    """
    Get camera properties from OpenCV and Windows.
    """
    props = {
        "opencv_index": str(camera_idx),
    }

    try:
        cap = cv2.VideoCapture(camera_idx)
        if cap.isOpened():
            # Get basic properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))

            props["resolution"] = f"{width}x{height}"
            props["fps"] = str(fps)

            # Try to get more detailed info
            try:
                fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
                props["fourcc"] = chr(fourcc & 255) + chr((fourcc >> 8) & 255) + chr((fourcc >> 16) & 255) + chr((fourcc >> 24) & 255)
            except Exception:
                pass

            cap.release()
    except Exception as e:
        props["error"] = str(e)

    return props


def get_linux_camera_fingerprints() -> List[Dict[str, str]]:
    """
    Get camera fingerprints on Linux using v4l2-ctl and /sys/class/video4linux.
    """
    fingerprints = []

    try:
        # Check if v4l2-ctl is available
        result = subprocess.run(
            ["v4l2-ctl", "--list-devices"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            output = result.stdout
            # Parse v4l2-ctl output
            lines = output.strip().split('\n')
            current_device = None

            for line in lines:
                if line and not line.startswith('\t'):
                    current_device = line
                elif line.startswith('\t') and current_device:
                    device_path = line.strip()
                    fingerprints.append({
                        "device": current_device,
                        "path": device_path,
                        "method": "v4l2",
                    })
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
        pass

    # Also check /sys/class/video4linux
    try:
        video_devices = Path("/sys/class/video4linux")
        if video_devices.exists():
            for device in sorted(video_devices.iterdir()):
                if device.is_symlink() or device.is_dir():
                    dev_name = device.name
                    dev_path = f"/dev/{dev_name}"

                    # Try to get device name from name file
                    name_file = device / "name"
                    if name_file.exists():
                        with open(name_file) as f:
                            name = f.read().strip()
                        fingerprints.append({
                            "device": name,
                            "path": dev_path,
                            "method": "sysfs",
                        })
    except Exception:
        pass

    return fingerprints


def get_macos_camera_fingerprints() -> List[Dict[str, str]]:
    """
    Get camera fingerprints on macOS using system_profiler.
    """
    fingerprints = []

    try:
        result = subprocess.run(
            ["system_profiler", "SPCameraDataType"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            output = result.stdout
            # Parse system_profiler output
            lines = output.split('\n')
            for i, line in enumerate(lines):
                if "Unique ID" in line:
                    unique_id = line.split(":", 1)[1].strip() if ":" in line else "unknown"
                    fingerprints.append({
                        "unique_id": unique_id,
                        "method": "system_profiler",
                    })
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
        pass

    return fingerprints


def main():
    """Main function to scan and display camera fingerprints."""
    print("=" * 80)
    print("CAMERA FINGERPRINT SCANNER - UNIQUE HARDWARE IDENTIFICATION")
    print("=" * 80)
    print()

    # Detect available cameras
    cameras = get_cameras_opencv()

    if not cameras:
        print("No cameras detected!")
        return 1

    print(f"Found {len(cameras)} camera index/indices available\n")

    # Get platform-specific fingerprints
    if sys.platform == "win32":
        print("Platform: Windows")
        print("-" * 80)

        # Get all USB camera devices
        usb_cameras = get_all_usb_cameras_windows()

        if usb_cameras:
            print(f"\n[USB CAMERAS - Total: {len(usb_cameras)}]\n")
            for idx, (device_path, info) in enumerate(usb_cameras.items(), 1):
                print(f"  Device {idx}:")
                print(f"    Friendly Name: {info['friendly_name']}")
                print(f"    Device Desc: {info['device_desc']}")
                print(f"    Vendor-Product ID: {info['vendor_product_id']}")
                print(f"    Full Path: {device_path}")
                print()
        else:
            print("\n[WARNING] No USB cameras found in registry. Checking OpenCV indices...\n")

        # Show OpenCV camera indices
        print(f"[CAMERA INDICES - Total: {len(cameras)}]\n")
        for idx, cam_id in enumerate(cameras):
            props = get_camera_properties_windows(cam_id)
            print(f"  Index {idx} (OpenCV {cam_id}):")
            for key, value in props.items():
                if key != "opencv_index":
                    print(f"    {key}: {value}")
            print()

        # Summary
        print("[SUMMARY]")
        print(f"  USB Devices Found: {len(usb_cameras)}")
        print(f"  Camera Indices Found: {len(cameras)}")
        if len(usb_cameras) != len(cameras):
            print(f"  WARNING: Mismatch between USB devices ({len(usb_cameras)}) and camera indices ({len(cameras)})")
            print(f"  This may indicate:")
            print(f"    - Some indices point to the same physical camera")
            print(f"    - USB cameras may not be properly enumerated")
            print(f"    - Try connecting/reconnecting cameras and rerunning")

    elif sys.platform == "linux":
        print("Platform: Linux")
        print("-" * 80)

        # Get v4l2 and sysfs info
        linux_fps = get_linux_camera_fingerprints()

        if linux_fps:
            print(f"\n[DETECTED CAMERAS - Total: {len(linux_fps)}]\n")
            for idx, fp in enumerate(linux_fps, 1):
                print(f"  Camera {idx}:")
                print(f"    Device: {fp.get('device', 'unknown')}")
                print(f"    Path: {fp.get('path', 'unknown')}")
                print(f"    Method: {fp.get('method')}")
                print()

        print(f"\n[CAMERA INDICES - Total: {len(cameras)}]\n")
        for idx, cam_id in enumerate(cameras):
            props = get_camera_properties_windows(cam_id)
            print(f"  Index {idx} (OpenCV {cam_id}):")
            for key, value in props.items():
                if key != "opencv_index":
                    print(f"    {key}: {value}")
            print()

    elif sys.platform == "darwin":
        print("Platform: macOS")
        print("-" * 80)

        macos_fps = get_macos_camera_fingerprints()
        if macos_fps:
            print(f"\n[SYSTEM CAMERAS - Total: {len(macos_fps)}]\n")
            for idx, fp in enumerate(macos_fps, 1):
                print(f"  Camera {idx}:")
                for key, value in fp.items():
                    print(f"    {key}: {value}")
                print()

        print(f"\n[CAMERA INDICES - Total: {len(cameras)}]\n")
        for idx, cam_id in enumerate(cameras):
            props = get_camera_properties_windows(cam_id)
            print(f"  Index {idx} (OpenCV {cam_id}):")
            for key, value in props.items():
                if key != "opencv_index":
                    print(f"    {key}: {value}")
            print()

    else:
        print(f"Platform: {sys.platform} (unsupported)")
        print("-" * 80)
        print(f"\n[CAMERA INDICES - Total: {len(cameras)}]\n")
        for idx, cam_id in enumerate(cameras):
            props = get_camera_properties_windows(cam_id)
            print(f"  Index {idx} (OpenCV {cam_id}):")
            for key, value in props.items():
                if key != "opencv_index":
                    print(f"    {key}: {value}")
            print()

    print("=" * 80)
    return 0


if __name__ == "__main__":
    sys.exit(main())
