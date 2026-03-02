import cv2
import numpy as np
import glob
import os
from collections import deque
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
)
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.table import Table

console = Console()

############
##### Sample imgs 1
chessboard_size = (11, 7)
square_size = 0.02208  # 22.08 mm per square (in meters)
image_size = (1025, 576)

left_images = sorted(glob.glob("calib/raw_images/left/*"))
right_images = sorted(glob.glob("calib/raw_images/right/*"))
############

##### Sample imgs 2
# chessboard_size = (10, 7)
# square_size = 0.025
# image_size = (800, 600)

# left_images = sorted(glob.glob("calib/l/*"))
# right_images = sorted(glob.glob("calib/r/*"))
############

console.print(f"[blue]Left images:[/blue] {len(left_images)}")
console.print(f"[blue]Right images:[/blue] {len(right_images)}")
assert len(left_images) == len(right_images), "Left/Right image counts must match!"

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 1e-2)

os.makedirs("debug", exist_ok=True)

objpoints, imgpoints_l, imgpoints_r = [], [], []


objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
objp[:, :2] = np.mgrid[0 : chessboard_size[0], 0 : chessboard_size[1]].T.reshape(-1, 2)
objp *= square_size

# Track last N saved files
LAST_N = 5
saved_files = deque(maxlen=LAST_N)
valid_pairs = 0
failed_reads = 0


def create_status_table():
    """Create a table showing the last N saved files."""
    table = Table(
        title=f"Last {LAST_N} Saved Files",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Index", style="cyan", width=6)
    table.add_column("Left File", style="green")
    table.add_column("Right File", style="green")
    table.add_column("Status", style="yellow")

    for item in saved_files:
        status_color = "green" if item["valid"] else "red"
        status_text = "✓ Valid" if item["valid"] else "✗ Invalid"
        table.add_row(
            str(item["idx"]),
            item["left"],
            item["right"],
            f"[{status_color}]{status_text}[/{status_color}]",
        )
    return table


def create_summary():
    """Create summary statistics panel."""
    summary_text = (
        f"[bold]Valid Stereo Pairs:[/bold] {valid_pairs}\n"
        f"[bold]Failed Reads:[/bold] {failed_reads}\n"
        f"[bold]Total Images:[/bold] {len(left_images)}"
    )
    return Panel(summary_text, title="Summary", border_style="blue")


# Main processing with progress bar and live UI
with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    TaskProgressColumn(),
    TimeRemainingColumn(),
    console=console,
) as progress:
    task = progress.add_task("[cyan]Processing images...", total=len(left_images))

    for i, (l_path, r_path) in enumerate(zip(left_images, right_images)):
        img_l = cv2.imread(l_path)
        img_r = cv2.imread(r_path)

        if img_l is None or img_r is None:
            failed_reads += 1
            saved_files.append(
                {
                    "idx": i,
                    "left": os.path.basename(l_path),
                    "right": os.path.basename(r_path),
                    "valid": False,
                }
            )
            progress.update(task, advance=1)
            continue

        gray_l = cv2.cvtColor(img_l, cv2.COLOR_BGR2GRAY)
        gray_r = cv2.cvtColor(img_r, cv2.COLOR_BGR2GRAY)

        flags = cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE + cv2.CALIB_CB_FILTER_QUADS
        ret_l, corners_l = cv2.findChessboardCorners(gray_l, chessboard_size, flags)
        ret_r, corners_r = cv2.findChessboardCorners(gray_r, chessboard_size, flags)

        vis_l = img_l.copy()
        vis_r = img_r.copy()

        if ret_l:
            corners_l = cv2.cornerSubPix(
                gray_l, corners_l, (15, 15), (-1, -1), criteria
            )
            cv2.drawChessboardCorners(vis_l, chessboard_size, corners_l, ret_l)
        if ret_r:
            corners_r = cv2.cornerSubPix(
                gray_r, corners_r, (15, 15), (-1, -1), criteria
            )
            cv2.drawChessboardCorners(vis_r, chessboard_size, corners_r, ret_r)

        l_file = f"debug/{i:02d}_L_{int(ret_l)}.png"
        r_file = f"debug/{i:02d}_R_{int(ret_r)}.png"
        cv2.imwrite(l_file, vis_l)
        cv2.imwrite(r_file, vis_r)

        is_valid = ret_l and ret_r
        if is_valid:
            valid_pairs += 1
            objpoints.append(objp)
            imgpoints_l.append(corners_l)
            imgpoints_r.append(corners_r)

        saved_files.append(
            {
                "idx": i,
                "left": os.path.basename(l_file),
                "right": os.path.basename(r_file),
                "valid": is_valid,
            }
        )

        progress.update(
            task,
            advance=1,
            description=f"[cyan]Processing {os.path.basename(l_path)}...",
        )

# Print final summary
console.print()
console.print(create_summary())
console.print()
console.print(create_status_table())
console.print()

console.print(f"[green]Valid stereo pairs:[/green] {len(objpoints)}")

# Generate stereo pair visualization with matching lines
if len(objpoints) > 0:
    # Find first valid pair index
    valid_pair_idx = None
    for i, (l_path, r_path) in enumerate(zip(left_images, right_images)):
        img_l = cv2.imread(l_path)
        img_r = cv2.imread(r_path)
        if img_l is None or img_r is None:
            continue

        gray_l = cv2.cvtColor(img_l, cv2.COLOR_BGR2GRAY)
        gray_r = cv2.cvtColor(img_r, cv2.COLOR_BGR2GRAY)

        flags = cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE + cv2.CALIB_CB_FILTER_QUADS
        ret_l, corners_l = cv2.findChessboardCorners(gray_l, chessboard_size, flags)
        ret_r, corners_r = cv2.findChessboardCorners(gray_r, chessboard_size, flags)

        if ret_l and ret_r:
            valid_pair_idx = i
            break

    if valid_pair_idx is not None:
        # Create side-by-side visualization with correspondence lines
        height = max(img_l.shape[0], img_r.shape[0])
        width = img_l.shape[1] + img_r.shape[1]
        vis = np.zeros((height, width, 3), dtype=np.uint8)

        # Place images side by side
        vis[: img_l.shape[0], : img_l.shape[1]] = img_l
        vis[: img_r.shape[0], img_l.shape[1] :] = img_r

        # Refine corners
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 1e-2)
        corners_l = cv2.cornerSubPix(gray_l, corners_l, (15, 15), (-1, -1), criteria)
        corners_r = cv2.cornerSubPix(gray_r, corners_r, (15, 15), (-1, -1), criteria)

        # Draw chessboard corners
        for corner in corners_l:
            x, y = corner.ravel()
            cv2.circle(vis, (int(x), int(y)), 4, (0, 255, 0), -1)

        offset_x = img_l.shape[1]
        for corner in corners_r:
            x, y = corner.ravel()
            cv2.circle(vis, (int(x) + offset_x, int(y)), 4, (0, 255, 255), -1)

        # Draw correspondence lines between matching corners
        for c_l, c_r in zip(corners_l, corners_r):
            x_l, y_l = c_l.ravel()
            x_r, y_r = c_r.ravel()
            cv2.line(
                vis,
                (int(x_l), int(y_l)),
                (int(x_r) + offset_x, int(y_r)),
                (255, 0, 0),
                1,
            )

        # Add labels
        cv2.putText(
            vis, "Left Camera", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
        )
        cv2.putText(
            vis,
            "Right Camera",
            (offset_x + 20, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 255),
            2,
        )
        cv2.putText(
            vis,
            f"Valid Stereo Pair #{valid_pair_idx} - {len(corners_l)} matched corners",
            (20, vis.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
        )

        # Save visualization
        output_path = "debug/stereo_pair_visualization.png"
        cv2.imwrite(output_path, vis)
        console.print(f"[cyan]Saved stereo pair visualization to {output_path}[/cyan]")

ret_l, K1, D1, rvecs_l, tvecs_l = cv2.calibrateCamera(
    objpoints, imgpoints_l, image_size, None, None
)
ret_r, K2, D2, rvecs_r, tvecs_r = cv2.calibrateCamera(
    objpoints, imgpoints_r, image_size, None, None
)

console.print(f"[yellow]Left reprojection error:[/yellow] {ret_l:.6f}")
console.print(f"[yellow]Right reprojection error:[/yellow] {ret_r:.6f}")

flags = cv2.CALIB_FIX_INTRINSIC  # keeps K1,D1,K2,D2 fixed; usually more stable
stereo_criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 1e-6)

ret_stereo, K1, D1, K2, D2, R, T, E, F = cv2.stereoCalibrate(
    objpoints,
    imgpoints_l,
    imgpoints_r,
    K1,
    D1,
    K2,
    D2,
    image_size,
    criteria=stereo_criteria,
    flags=flags,
)

console.print(f"[green]Stereo calibration RMS error:[/green] {ret_stereo:.6f}")
console.print(f"[blue]Translation T (meters):[/blue]")
console.print(T)

R1, R2, P1, P2, Q, roi1, roi2 = cv2.stereoRectify(
    K1,
    D1,
    K2,
    D2,
    image_size,
    R,
    T,
    flags=cv2.CALIB_ZERO_DISPARITY,
    alpha=0,  # 0 = crop to valid pixels; 1 = keep all pixels (black borders)
)

map1x, map1y = cv2.initUndistortRectifyMap(K1, D1, R1, P1, image_size, cv2.CV_32FC1)
map2x, map2y = cv2.initUndistortRectifyMap(K2, D2, R2, P2, image_size, cv2.CV_32FC1)

np.savez(
    "stereo_calib.npz",
    K1=K1,
    D1=D1,
    K2=K2,
    D2=D2,
    R=R,
    T=T,
    R1=R1,
    R2=R2,
    P1=P1,
    P2=P2,
    Q=Q,
    map1x=map1x,
    map1y=map1y,
    map2x=map2x,
    map2y=map2y,
)

console.print(f"[bold green]✓ Saved to stereo_calib.npz[/bold green]")
