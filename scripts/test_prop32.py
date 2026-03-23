import cv2
import os
from dotenv import load_dotenv
import time

load_dotenv()

LEFT_CAMERA_INDEX = int(os.getenv("LEFT_CAMERA_INDEX", 0))

cap = cv2.VideoCapture(LEFT_CAMERA_INDEX)

print(f"Testing Property 32 (CV_CAP_PROP_FOCUS) on camera {LEFT_CAMERA_INDEX}\n")

# First disable autofocus more aggressively
print("Attempting to disable autofocus (property 38)...")
for value in [0.0, 1.0]:
    result = cap.set(38, value)
    print(f"  set(38, {value}): {result}")
    time.sleep(0.5)

# Check current focus value
current = cap.get(32)
print(f"\nCurrent focus (property 32): {current}")

print("\nInteractive focus test:")
print("  K: Increase focus")
print("  J: Decrease focus")
print("  R: Reset to 0")
print("  Q: Quit\n")

current_focus = float(current)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Display frame with info
    cv2.putText(frame, f"Focus value: {current_focus:.0f}", (10, 30),
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.putText(frame, "K=increase, J=decrease, R=reset, Q=quit", (10, 70),
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)

    cv2.imshow("Focus Test - Property 32", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == ord('Q'):
        break
    elif key == ord('k') or key == ord('K'):
        current_focus = min(255, current_focus + 10)
        result = cap.set(32, current_focus)
        read_back = cap.get(32)
        print(f"Focus UP: set to {current_focus:.0f}, result={result}, read_back={read_back:.0f}")
    elif key == ord('j') or key == ord('J'):
        current_focus = max(0, current_focus - 10)
        result = cap.set(32, current_focus)
        read_back = cap.get(32)
        print(f"Focus DOWN: set to {current_focus:.0f}, result={result}, read_back={read_back:.0f}")
    elif key == ord('r') or key == ord('R'):
        current_focus = 0
        result = cap.set(32, current_focus)
        read_back = cap.get(32)
        print(f"Focus RESET to 0, result={result}, read_back={read_back:.0f}")

cv2.destroyAllWindows()
cap.release()

print("\nDid the image focus/blur change as you adjusted the values?")
