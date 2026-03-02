import cv2
import time

def test_camera_ports(max_index=10):
    """Test available USB camera ports and display their feed."""
    cameras = {}

    print("Testing camera ports...")
    for i in range(max_index):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                cameras[i] = cap
                print(f"✓ Camera found at index {i}")
            else:
                cap.release()
        else:
            cap.release()

    if not cameras:
        print("No cameras found!")
        return

    print(f"\nFound {len(cameras)} camera(s) at indices: {list(cameras.keys())}")

    # Display each camera feed
    print("\nDisplaying feeds (press 'q' to exit, 'n' for next camera)...")
    for idx in cameras:
        cap = cameras[idx]
        print(f"\nShowing camera {idx}...")
        start_time = time.time()

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            cv2.putText(frame, f"Camera {idx}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow(f"Camera {idx}", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                cv2.destroyAllWindows()
                for c in cameras.values():
                    c.release()
                return
            elif key == ord('n'):
                cv2.destroyAllWindows()
                break

            if time.time() - start_time > 10:  # Auto-advance after 10s
                cv2.destroyAllWindows()
                break

    for cap in cameras.values():
        cap.release()

if __name__ == "__main__":
    test_camera_ports()
