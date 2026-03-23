import cv2
import os
from dotenv import load_dotenv

load_dotenv()

LEFT_CAMERA_INDEX = int(os.getenv("LEFT_CAMERA_INDEX", 0))

cap = cv2.VideoCapture(LEFT_CAMERA_INDEX)

print(f"Scanning ALL properties (0-255) for camera {LEFT_CAMERA_INDEX}\n")
print("Properties that return >= 0 (settable/readable):\n")

found_props = []
for prop_id in range(256):
    try:
        val = cap.get(prop_id)
        if val >= 0 and val < 1000:  # Filter out strange values
            found_props.append((prop_id, val))
            print(f"  Property {prop_id:3d}: {val}")
    except:
        pass

print(f"\nTotal properties found: {len(found_props)}")
print("\nProperties to try manually:")
print("  Try: cap.set(prop_id, 0) and cap.set(prop_id, 255)")
print("  to see what each one controls")

cap.release()
