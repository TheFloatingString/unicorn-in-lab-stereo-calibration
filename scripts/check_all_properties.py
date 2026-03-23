import cv2
import os
from dotenv import load_dotenv

load_dotenv()

LEFT_CAMERA_DEVICE_ID = os.getenv("LEFT_CAMERA_DEVICE_ID")
LEFT_CAMERA_INDEX = int(os.getenv("LEFT_CAMERA_INDEX", 0))

cap = cv2.VideoCapture(LEFT_CAMERA_INDEX)

print(f"Checking all camera properties for camera {LEFT_CAMERA_INDEX}")
print(f"Device: {LEFT_CAMERA_DEVICE_ID}\n")

# Check properties 0-50
for prop_id in range(50):
    try:
        val = cap.get(prop_id)
        if val >= 0 or val == -1:
            # Map common property IDs to names
            prop_names = {
                0: "CV_CAP_PROP_POS_MSEC",
                1: "CV_CAP_PROP_POS_FRAMES",
                2: "CV_CAP_PROP_POS_AVI_RATIO",
                3: "CV_CAP_PROP_FRAME_WIDTH",
                4: "CV_CAP_PROP_FRAME_HEIGHT",
                5: "CV_CAP_PROP_FPS",
                6: "CV_CAP_PROP_FOURCC",
                10: "CV_CAP_PROP_BRIGHTNESS",
                11: "CV_CAP_PROP_CONTRAST",
                12: "CV_CAP_PROP_SATURATION",
                13: "CV_CAP_PROP_HUE",
                14: "CV_CAP_PROP_GAIN",
                15: "CV_CAP_PROP_EXPOSURE",
                17: "CV_CAP_PROP_CONVERT_RGB",
                32: "CV_CAP_PROP_FOCUS",  # Actually this might be focus mode
                38: "CV_CAP_PROP_AUTOFOCUS",
                39: "CV_CAP_PROP_AUTO_EXPOSURE",
                44: "CV_CAP_PROP_FOCUS (alt)",
                175: "CV_CAP_PROP_FOCUS_ALT",
            }
            prop_name = prop_names.get(prop_id, f"Unknown prop {prop_id}")
            print(f"  Property {prop_id:3d} ({prop_name:30s}): {val}")
    except:
        pass

cap.release()
