import cv2
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import time

load_dotenv()

LEFT_CAMERA_DEVICE_ID = os.getenv("LEFT_CAMERA_DEVICE_ID")
RIGHT_CAMERA_DEVICE_ID = os.getenv("RIGHT_CAMERA_DEVICE_ID")

def get_camera_index_from_device_id(target_device_id: str) -> int:
    """Find camera index from device ID."""
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

# Determine camera indices
if LEFT_CAMERA_DEVICE_ID and RIGHT_CAMERA_DEVICE_ID:
    LEFT_CAMERA_INDEX = get_camera_index_from_device_id(LEFT_CAMERA_DEVICE_ID)
    RIGHT_CAMERA_INDEX = get_camera_index_from_device_id(RIGHT_CAMERA_DEVICE_ID)

    if LEFT_CAMERA_INDEX == -1 or RIGHT_CAMERA_INDEX == -1:
        print("Warning: Could not find cameras by device ID. Using fallback indices.")
        LEFT_CAMERA_INDEX = int(os.getenv("LEFT_CAMERA_INDEX", 0))
        RIGHT_CAMERA_INDEX = int(os.getenv("RIGHT_CAMERA_INDEX", 2))
else:
    LEFT_CAMERA_INDEX = int(os.getenv("LEFT_CAMERA_INDEX", 0))
    RIGHT_CAMERA_INDEX = int(os.getenv("RIGHT_CAMERA_INDEX", 2))

print(f"Opening cameras...")
print(f"  Left index: {LEFT_CAMERA_INDEX}, Device: {LEFT_CAMERA_DEVICE_ID}")
print(f"  Right index: {RIGHT_CAMERA_INDEX}, Device: {RIGHT_CAMERA_DEVICE_ID}")

cap_left = cv2.VideoCapture(LEFT_CAMERA_INDEX)
cap_right = cv2.VideoCapture(RIGHT_CAMERA_INDEX)

if not (cap_left.isOpened() and cap_right.isOpened()):
    print("Error: Could not open cameras")
    sys.exit(1)

print("Cameras opened successfully")
print("\nWaiting for cameras to warm up...")

# Wait longer and read frames to let cameras adjust
print("Reading frames to initialize...")
for i in range(30):
    ret_l, frame_l = cap_left.read()
    ret_r, frame_r = cap_right.read()

    if i % 10 == 0:
        print(f"  Frame {i}: left={ret_l}, right={ret_r}, left shape={frame_l.shape if ret_l else 'None'}")

    if ret_l and ret_r:
        # Check if frames are completely black
        avg_l = frame_l.mean()
        avg_r = frame_r.mean()
        if i % 10 == 0:
            print(f"    Brightness - left avg: {avg_l:.1f}, right avg: {avg_r:.1f}")

print("\nDisplaying live feed (press Q to quit)...")
print("Watch for black frames or if images appear")

while True:
    ret_l, frame_left = cap_left.read()
    ret_r, frame_right = cap_right.read()

    if not (ret_l and ret_r):
        print("Error reading frames")
        break

    # Check brightness
    avg_l = frame_left.mean()
    avg_r = frame_right.mean()

    cv2.putText(frame_left, f"LEFT - Brightness: {avg_l:.1f}", (10, 30),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv2.putText(frame_right, f"RIGHT - Brightness: {avg_r:.1f}", (10, 30),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    combined = cv2.hconcat([frame_left, frame_right])
    cv2.imshow("Diagnostic Feed (L | R)", combined)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == ord('Q'):
        break

cap_left.release()
cap_right.release()
cv2.destroyAllWindows()
print("Diagnostic complete")
