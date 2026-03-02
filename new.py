import cv2
import numpy as np

############
# -------- SETTINGS --------
##### Sample imgs 1
LEFT_IMG  = "calib/Im_L_15.png"
RIGHT_IMG = "calib/Im_R_15.png"

##### Sample imgs 2
# LEFT_IMG  = "calib/frame381_l.jpg"
# RIGHT_IMG = "calib/frame381_r.jpg"
############

CALIB_FILE = "stereo_calib.npz"
LINE_SPACING = 40   # pixels

# -------- LOAD CALIBRATION --------
data = np.load(CALIB_FILE)

map1x = data["map1x"]
map1y = data["map1y"]
map2x = data["map2x"]
map2y = data["map2y"]

# -------- LOAD IMAGES --------
img_l = cv2.imread(LEFT_IMG)
img_r = cv2.imread(RIGHT_IMG)

if img_l is None or img_r is None:
    raise RuntimeError("Failed to load left or right image")

# -------- RECTIFY --------
rect_l = cv2.remap(img_l, map1x, map1y, cv2.INTER_LINEAR)
rect_r = cv2.remap(img_r, map2x, map2y, cv2.INTER_LINEAR)

# -------- DRAW HORIZONTAL GUIDE LINES --------
h, w = rect_l.shape[:2]

for y in range(0, h, LINE_SPACING):
    cv2.line(rect_l, (0, y), (w, y), (0, 255, 0), 1)
    cv2.line(rect_r, (0, y), (w, y), (0, 255, 0), 1)

# -------- COMBINE SIDE-BY-SIDE --------
combined = np.hstack((rect_l, rect_r))

# -------- SHOW --------
cv2.imshow("Rectified Left | Rectified Right", combined)
cv2.waitKey(0)
cv2.destroyAllWindows()
