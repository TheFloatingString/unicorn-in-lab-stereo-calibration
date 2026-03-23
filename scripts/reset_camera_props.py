import cv2
import os
import sys
from dotenv import load_dotenv

load_dotenv()

LEFT_CAMERA_DEVICE_ID = os.getenv("LEFT_CAMERA_DEVICE_ID")
RIGHT_CAMERA_DEVICE_ID = os.getenv("RIGHT_CAMERA_DEVICE_ID")

def get_camera_index_from_device_id(target_device_id: str) -> int:
    """Find camera index from device ID (cross-platform)."""
    if not target_device_id or target_device_id == "unknown":
        return -1

    if sys.platform == "win32":
        from get_camera_ids import get_all_usb_cameras_windows, get_cameras_opencv
        usb_cameras = get_all_usb_cameras_windows()
        device_list = list(usb_cameras.values())
        available_cameras = get_cameras_opencv()

        for idx in available_cameras:
            if idx < len(device_list):
                device_info = device_list[idx]
                if device_info.get("vendor_product_id") == target_device_id:
                    return idx
    return -1

def reset_camera_properties(cap, name):
    """Reset camera to default properties."""
    print(f"\nResetting {name}...")

    # Default values for common USB camera properties
    defaults = {
        10: 128,      # Brightness
        11: 32,       # Contrast
        12: 64,       # Saturation
        13: 0,        # Hue
        14: 4,        # Gain
        15: 100,      # Exposure
        32: 0,        # Focus (manual mode, minimum)
        38: 1,        # AutoFocus (on)
    }

    for prop_id, default_value in defaults.items():
        try:
            result = cap.set(prop_id, default_value)
            current = cap.get(prop_id)
            status = "OK" if result else "FAIL"
            print(f"  Property {prop_id:2d}: set to {default_value:3d}, read back {current:6.1f} ({status})")
        except Exception as e:
            print(f"  Property {prop_id:2d}: Error - {e}")

    print(f"{name} reset complete!")

def main():
    # Determine camera indices
    if LEFT_CAMERA_DEVICE_ID and RIGHT_CAMERA_DEVICE_ID:
        LEFT_CAMERA_INDEX = get_camera_index_from_device_id(LEFT_CAMERA_DEVICE_ID)
        RIGHT_CAMERA_INDEX = get_camera_index_from_device_id(RIGHT_CAMERA_DEVICE_ID)

        if LEFT_CAMERA_INDEX == -1:
            LEFT_CAMERA_INDEX = int(os.getenv("LEFT_CAMERA_INDEX", 0))
        if RIGHT_CAMERA_INDEX == -1:
            RIGHT_CAMERA_INDEX = int(os.getenv("RIGHT_CAMERA_INDEX", 2))
    else:
        LEFT_CAMERA_INDEX = int(os.getenv("LEFT_CAMERA_INDEX", 0))
        RIGHT_CAMERA_INDEX = int(os.getenv("RIGHT_CAMERA_INDEX", 2))

    print("Opening cameras for reset...")
    print(f"  Left: Index {LEFT_CAMERA_INDEX}, Device: {LEFT_CAMERA_DEVICE_ID}")
    print(f"  Right: Index {RIGHT_CAMERA_INDEX}, Device: {RIGHT_CAMERA_DEVICE_ID}")

    # Open cameras
    cap_left = cv2.VideoCapture(LEFT_CAMERA_INDEX)
    cap_right = cv2.VideoCapture(RIGHT_CAMERA_INDEX)

    if not (cap_left.isOpened() and cap_right.isOpened()):
        print("\nError: Could not open cameras")
        return

    # Reset properties
    reset_camera_properties(cap_left, "LEFT Camera")
    reset_camera_properties(cap_right, "RIGHT Camera")

    # Release cameras
    cap_left.release()
    cap_right.release()

    print("\nAll camera properties reset to defaults!")

if __name__ == "__main__":
    main()
