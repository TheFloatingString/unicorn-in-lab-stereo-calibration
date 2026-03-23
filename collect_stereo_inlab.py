import cv2
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get stored device IDs from .env
LEFT_CAMERA_DEVICE_ID = os.getenv("LEFT_CAMERA_DEVICE_ID")
RIGHT_CAMERA_DEVICE_ID = os.getenv("RIGHT_CAMERA_DEVICE_ID")

def get_camera_index_from_device_id(target_device_id: str) -> int:
    """
    Find camera index that corresponds to the given device ID.
    Works cross-platform (Windows, Linux, macOS).
    Returns the index, or -1 if not found.
    """
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
                vendor_product_id = device_info.get("vendor_product_id", "")
                if vendor_product_id == target_device_id:
                    return idx

    elif sys.platform == "linux":
        from get_camera_ids import get_linux_camera_fingerprints, get_cameras_opencv
        linux_fps = get_linux_camera_fingerprints()
        available_cameras = get_cameras_opencv()

        for idx in available_cameras:
            if idx < len(linux_fps):
                device_info = linux_fps[idx]
                # Try to match by path or device name
                if (device_info.get("path") == target_device_id or
                    device_info.get("device") == target_device_id):
                    return idx

    elif sys.platform == "darwin":
        from get_camera_ids import get_macos_camera_fingerprints, get_cameras_opencv
        macos_fps = get_macos_camera_fingerprints()
        available_cameras = get_cameras_opencv()

        for idx in available_cameras:
            if idx < len(macos_fps):
                device_info = macos_fps[idx]
                if device_info.get("unique_id") == target_device_id:
                    return idx

    return -1

# Determine camera indices
if LEFT_CAMERA_DEVICE_ID and RIGHT_CAMERA_DEVICE_ID:
    # Try to find indices from stored device IDs
    LEFT_CAMERA_INDEX = get_camera_index_from_device_id(LEFT_CAMERA_DEVICE_ID)
    RIGHT_CAMERA_INDEX = get_camera_index_from_device_id(RIGHT_CAMERA_DEVICE_ID)

    if LEFT_CAMERA_INDEX == -1 or RIGHT_CAMERA_INDEX == -1:
        print("Warning: Could not find cameras by device ID. Using fallback indices.")
        try:
            LEFT_CAMERA_INDEX = int(os.getenv("LEFT_CAMERA_INDEX", 0))
        except (TypeError, ValueError):
            LEFT_CAMERA_INDEX = 0

        try:
            RIGHT_CAMERA_INDEX = int(os.getenv("RIGHT_CAMERA_INDEX", 2))
        except (TypeError, ValueError):
            RIGHT_CAMERA_INDEX = 2
else:
    # Fallback to stored indices if device IDs not available
    try:
        LEFT_CAMERA_INDEX = int(os.getenv("LEFT_CAMERA_INDEX", 0))
    except (TypeError, ValueError):
        LEFT_CAMERA_INDEX = 0

    try:
        RIGHT_CAMERA_INDEX = int(os.getenv("RIGHT_CAMERA_INDEX", 2))
    except (TypeError, ValueError):
        RIGHT_CAMERA_INDEX = 2

# Create timestamped subdirectory for this capture session
session_timestamp = datetime.now().strftime("%Y_mar_%d_%I%p").lower()
OUTPUT_DIR = f"calib/raw_images/{session_timestamp}"
os.makedirs(f"{OUTPUT_DIR}/left", exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/right", exist_ok=True)

def capture_stereo_pair(cap_left, cap_right, frame_count):
    """Capture a stereo pair and save to disk."""
    ret_l, frame_left = cap_left.read()
    ret_r, frame_right = cap_right.read()

    if not (ret_l and ret_r):
        return False

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]

    left_path = f"{OUTPUT_DIR}/left/{frame_count:04d}_{timestamp}.jpg"
    right_path = f"{OUTPUT_DIR}/right/{frame_count:04d}_{timestamp}.jpg"

    cv2.imwrite(left_path, frame_left)
    cv2.imwrite(right_path, frame_right)

    print(f"Captured pair {frame_count}")
    return True

def main():
    cap_left = cv2.VideoCapture(LEFT_CAMERA_INDEX)
    cap_right = cv2.VideoCapture(RIGHT_CAMERA_INDEX)

    if not (cap_left.isOpened() and cap_right.isOpened()):
        print("Error: Could not open cameras")
        print(f"  Left index: {LEFT_CAMERA_INDEX}, Device: {LEFT_CAMERA_DEVICE_ID}")
        print(f"  Right index: {RIGHT_CAMERA_INDEX}, Device: {RIGHT_CAMERA_DEVICE_ID}")
        return

    print(f"Cameras opened - Left index: {LEFT_CAMERA_INDEX}, Right index: {RIGHT_CAMERA_INDEX}")
    print(f"Left device: {LEFT_CAMERA_DEVICE_ID}")
    print(f"Right device: {RIGHT_CAMERA_DEVICE_ID}")
    print("Press 'c' to capture, 'q' to quit")

    frame_count = 0

    while True:
        ret_l, frame_left = cap_left.read()
        ret_r, frame_right = cap_right.read()

        if not (ret_l and ret_r):
            break

        # Display side-by-side
        combined = cv2.hconcat([frame_left, frame_right])
        cv2.imshow("Stereo Feed (L | R)", combined)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            if capture_stereo_pair(cap_left, cap_right, frame_count):
                frame_count += 1

    cap_left.release()
    cap_right.release()
    cv2.destroyAllWindows()
    print(f"Captured {frame_count} stereo pairs")

if __name__ == "__main__":
    main()
