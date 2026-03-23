import cv2
import time
import sys
import os
from pathlib import Path
from get_camera_ids import get_all_usb_cameras_windows, get_cameras_opencv

def load_env_file():
    """Load existing .env file, create if it doesn't exist."""
    env_path = Path(".env")
    env_vars = {}

    # Create empty .env file if it doesn't exist
    if not env_path.exists():
        env_path.touch()
        print("Created .env file")

    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "=" in line:
                        key, value = line.split("=", 1)
                        env_vars[key.strip()] = value.strip()
    return env_vars, env_path

def save_camera_id_to_env(position: str, camera_idx: int, device_id: str):
    """Save camera index and device ID to .env file."""
    env_vars, env_path = load_env_file()

    if position == "LEFT":
        env_vars["LEFT_CAMERA_INDEX"] = str(camera_idx)
        env_vars["LEFT_CAMERA_DEVICE_ID"] = device_id
        print(f"\n✓ Saved LEFT camera: Index {camera_idx}, Device: {device_id}")
    elif position == "RIGHT":
        env_vars["RIGHT_CAMERA_INDEX"] = str(camera_idx)
        env_vars["RIGHT_CAMERA_DEVICE_ID"] = device_id
        print(f"\n✓ Saved RIGHT camera: Index {camera_idx}, Device: {device_id}")

    # Write back to .env
    with open(env_path, "w") as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")

    print(f"  Saved to .env")

def get_camera_device_id_for_index(camera_idx: int, usb_cameras: dict) -> str:
    """Map camera index to hardware device identifier (platform-specific)."""
    device_list = list(usb_cameras.values())

    if camera_idx < len(device_list):
        device_info = device_list[camera_idx]
        # Return platform-specific identifier
        if sys.platform == "win32":
            return device_info.get("vendor_product_id", "unknown")
        elif sys.platform == "linux":
            return device_info.get("path", device_info.get("device", "unknown"))
        elif sys.platform == "darwin":
            return device_info.get("unique_id", "unknown")

    return "unknown"

def test_camera_ports(max_index=10):
    """Test available USB camera ports and display their feed."""
    cameras = {}

    # Get hardware IDs for all cameras (platform-specific)
    usb_cameras = {}
    if sys.platform == "win32":
        usb_cameras = get_all_usb_cameras_windows()
    elif sys.platform == "linux":
        from get_camera_ids import get_linux_camera_fingerprints
        linux_fps = get_linux_camera_fingerprints()
        usb_cameras = {fp.get("path", f"video{i}"): fp for i, fp in enumerate(linux_fps)}
    elif sys.platform == "darwin":
        from get_camera_ids import get_macos_camera_fingerprints
        macos_fps = get_macos_camera_fingerprints()
        usb_cameras = {fp.get("unique_id", f"camera{i}"): fp for i, fp in enumerate(macos_fps)}

    print("Testing camera ports...")
    available_cameras = get_cameras_opencv()

    for i in available_cameras:
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                cameras[i] = cap
                device_id = get_camera_device_id_for_index(i, usb_cameras)
                print(f"Camera found at index {i} - Device ID: {device_id}")
            else:
                cap.release()
        else:
            cap.release()

    if not cameras:
        print("No cameras found!")
        return

    print(f"Found {len(cameras)} camera(s) at indices: {list(cameras.keys())}")
    print("\nControls:")
    print("  'q' = quit")
    print("  'n' = next camera")
    print("  'L' = save as LEFT camera to .env")
    print("  'R' = save as RIGHT camera to .env")

    # Display each camera feed
    print("\nDisplaying feeds...")
    for idx in cameras:
        cap = cameras[idx]
        device_id = get_camera_device_id_for_index(idx, usb_cameras)
        print(f"\nShowing camera {idx} (Device: {device_id})...")
        start_time = time.time()

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Display camera index and device ID on frame
            cv2.putText(frame, f"Camera Index: {idx}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(frame, f"Device ID: {device_id}", (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, "Press: L=Left, R=Right, N=Next, Q=Quit", (10, 110),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)

            cv2.imshow(f"Camera {idx}", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == ord('Q'):
                cv2.destroyAllWindows()
                for c in cameras.values():
                    c.release()
                return
            elif key == ord('n') or key == ord('N'):
                cv2.destroyAllWindows()
                break
            elif key == ord('l') or key == ord('L'):
                save_camera_id_to_env("LEFT", idx, device_id)
            elif key == ord('r') or key == ord('R'):
                save_camera_id_to_env("RIGHT", idx, device_id)

            if time.time() - start_time > 10:  # Auto-advance after 10s
                cv2.destroyAllWindows()
                break

    for cap in cameras.values():
        cap.release()

if __name__ == "__main__":
    test_camera_ports()
