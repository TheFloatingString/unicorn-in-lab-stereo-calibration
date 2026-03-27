#include <opencv2/opencv.hpp>
#include <cnpy.h>
#include <string>
#include <stdexcept>
#include <iostream>

// -------- SETTINGS --------
// Sample imgs 1
// const std::string LEFT_IMG  = "../calib/Im_L_15.png";
// const std::string RIGHT_IMG = "../calib/Im_R_15.png";

// Sample imgs 2
// const std::string LEFT_IMG  = "../calib/frame381_l.jpg";
// const std::string RIGHT_IMG = "../calib/frame381_r.jpg";

const std::string LEFT_IMG   = "../calib/MAR_03_L.jpg";
const std::string RIGHT_IMG  = "../calib/MAR_03_R.jpg";
const std::string CALIB_FILE = "../stereo_calib.npz";
const int LINE_SPACING = 40; // pixels

// Helper: load a 2-D float array from cnpy into a cv::Mat
static cv::Mat npz_to_mat(const cnpy::NpyArray& arr) {
    if (arr.shape.size() != 2)
        throw std::runtime_error("Expected 2-D array");

    int rows = static_cast<int>(arr.shape[0]);
    int cols = static_cast<int>(arr.shape[1]);

    // cnpy stores as float by default; clone so we own the memory
    cv::Mat m(rows, cols, CV_32F);
    const float* src = arr.data<float>();
    std::copy(src, src + rows * cols, m.ptr<float>());
    return m;
}

int main() {
try {
    // -------- LOAD CALIBRATION --------
    cnpy::npz_t data = cnpy::npz_load(CALIB_FILE);

    cv::Mat map1x = npz_to_mat(data.at("map1x"));
    cv::Mat map1y = npz_to_mat(data.at("map1y"));
    cv::Mat map2x = npz_to_mat(data.at("map2x"));
    cv::Mat map2y = npz_to_mat(data.at("map2y"));

    // -------- LOAD IMAGES --------
    cv::Mat img_l = cv::imread(LEFT_IMG);
    cv::Mat img_r = cv::imread(RIGHT_IMG);

    if (img_l.empty() || img_r.empty())
        throw std::runtime_error("Failed to load left or right image");

    // -------- RECTIFY --------
    cv::Mat rect_l, rect_r;
    cv::remap(img_l, rect_l, map1x, map1y, cv::INTER_LINEAR);
    cv::remap(img_r, rect_r, map2x, map2y, cv::INTER_LINEAR);

    // -------- DRAW HORIZONTAL GUIDE LINES --------
    int h = rect_l.rows;
    int w = rect_l.cols;

    for (int y = 0; y < h; y += LINE_SPACING) {
        cv::line(rect_l, {0, y}, {w, y}, {0, 255, 255}, 1);
        cv::line(rect_r, {0, y}, {w, y}, {0, 255, 255}, 1);
    }

    // -------- COMBINE SIDE-BY-SIDE --------
    cv::Mat combined;
    cv::hconcat(rect_l, rect_r, combined);

    // -------- SHOW --------
    cv::imshow("Rectified Left <|> Rectified Right", combined);
    cv::waitKey(0);
    cv::destroyAllWindows();

    return 0;
} catch (const std::exception& e) {
    std::cerr << "Error: " << e.what() << std::endl;
    return 1;
}
}
