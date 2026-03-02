import cv2
import os
from datetime import datetime

LEFT_CAMERA_INDEX = 2
RIGHT_CAMERA_INDEX = 1

OUTPUT_DIR = "calib/raw_images"
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
        return

    print(f"Cameras opened - Left: {LEFT_CAMERA_INDEX}, Right: {RIGHT_CAMERA_INDEX}")
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
