import cv2
import os
import sys
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
    try:
        LEFT_CAMERA_INDEX = int(os.getenv("LEFT_CAMERA_INDEX", 0))
    except (TypeError, ValueError):
        LEFT_CAMERA_INDEX = 0

    try:
        RIGHT_CAMERA_INDEX = int(os.getenv("RIGHT_CAMERA_INDEX", 2))
    except (TypeError, ValueError):
        RIGHT_CAMERA_INDEX = 2

def disable_auto_focus(cap):
    """Disable auto-focus to allow manual focus control."""
    results = []

    # Try to disable auto-focus (property 38)
    try:
        result = cap.set(38, 0)
        results.append(f"Autofocus disable: {result}")
    except Exception as e:
        results.append(f"Autofocus disable failed: {e}")

    # Try setting focus mode to manual (property 32)
    try:
        result = cap.set(32, 0)
        results.append(f"Focus mode to manual: {result}")
    except Exception as e:
        results.append(f"Focus mode failed: {e}")

    return results

def set_camera_focus(cap, focus_value):
    """Set camera focus using property 10 (most reliable)."""
    try:
        # Property 10 is the focus property for most USB cameras
        result = cap.set(10, focus_value)
        return result
    except Exception as e:
        return False

def get_camera_focus(cap):
    """Get current camera focus value."""
    try:
        # Property 10 is the focus property
        focus = cap.get(10)
        return focus if focus >= 0 else None
    except Exception:
        return None

def check_camera_properties(cap, name):
    """Check what focus-related properties are supported."""
    properties_to_check = [
        (10, "Focus (alt)"),
        (32, "Focus Mode"),
        (38, "AutoFocus"),
        (39, "AF Trigger"),
        (175, "Focus"),
    ]

    print(f"\n{name} Properties:")
    for prop_id, prop_name in properties_to_check:
        try:
            val = cap.get(prop_id)
            if val >= 0:
                print(f"  {prop_name} ({prop_id}): {val} (AVAILABLE)")
            else:
                print(f"  {prop_name} ({prop_id}): {val} (not available)")
        except:
            print(f"  {prop_name} ({prop_id}): Not supported")

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
    print()
    print("Controls:")
    print("  D = Decrease focus (unfocus) LEFT camera")
    print("  F = Increase focus (focus more) LEFT camera")
    print("  J = Decrease focus (unfocus) RIGHT camera")
    print("  K = Increase focus (focus more) RIGHT camera")
    print("  Q = Quit")
    print()

    # Disable auto-focus to enable manual focus control
    # Check camera properties
    check_camera_properties(cap_left, "LEFT Camera")
    check_camera_properties(cap_right, "RIGHT Camera")

    print("\nDisabling auto-focus...")
    left_results = disable_auto_focus(cap_left)
    right_results = disable_auto_focus(cap_right)

    for result in left_results:
        print(f"  LEFT: {result}")
    for result in right_results:
        print(f"  RIGHT: {result}")

    # Initialize focus values
    left_focus = 255
    right_focus = 255
    focus_step = 10

    # Try to set initial focus
    print("Setting initial focus...")
    set_camera_focus(cap_left, left_focus)
    set_camera_focus(cap_right, right_focus)

    # Read a few frames to let settings apply
    for _ in range(5):
        cap_left.read()
        cap_right.read()

    while True:
        ret_l, frame_left = cap_left.read()
        ret_r, frame_right = cap_right.read()

        if not (ret_l and ret_r):
            print("Error reading frames")
            break

        # Add text info to frames
        left_focus_display = get_camera_focus(cap_left)
        right_focus_display = get_camera_focus(cap_right)

        cv2.putText(frame_left, f"LEFT - Focus: {left_focus_display if left_focus_display is not None else left_focus:.0f}",
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame_left, "D=unfocus, F=focus", (10, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)

        cv2.putText(frame_right, f"RIGHT - Focus: {right_focus_display if right_focus_display is not None else right_focus:.0f}",
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame_right, "J=unfocus, K=focus", (10, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)

        # Display side-by-side
        combined = cv2.hconcat([frame_left, frame_right])
        cv2.imshow("Stereo Focus Test (L | R)", combined)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == ord('Q'):
            break
        elif key == ord('d') or key == ord('D'):
            left_focus = max(0, left_focus - focus_step)
            result = set_camera_focus(cap_left, left_focus)
            print(f"Left focus: {left_focus} (set: {result})")
        elif key == ord('f') or key == ord('F'):
            left_focus = min(255, left_focus + focus_step)
            result = set_camera_focus(cap_left, left_focus)
            print(f"Left focus: {left_focus} (set: {result})")
        elif key == ord('j') or key == ord('J'):
            right_focus = max(0, right_focus - focus_step)
            result = set_camera_focus(cap_right, right_focus)
            print(f"Right focus: {right_focus} (set: {result})")
        elif key == ord('k') or key == ord('K'):
            right_focus = min(255, right_focus + focus_step)
            result = set_camera_focus(cap_right, right_focus)
            print(f"Right focus: {right_focus} (set: {result})")

    cap_left.release()
    cap_right.release()
    cv2.destroyAllWindows()
    print("Focus test ended")

if __name__ == "__main__":
    main()
