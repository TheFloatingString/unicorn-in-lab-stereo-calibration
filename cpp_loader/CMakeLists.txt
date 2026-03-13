cmake_minimum_required(VERSION 3.16)
project(stereo_rectify CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(OpenCV REQUIRED COMPONENTS core imgproc highgui imgcodecs)

# cnpy for loading .npz files
include(FetchContent)
FetchContent_Declare(
    cnpy
    GIT_REPOSITORY https://github.com/rogersce/cnpy.git
    GIT_TAG        master
)
FetchContent_MakeAvailable(cnpy)

add_executable(stereo_rectify main.cpp)

target_include_directories(stereo_rectify PRIVATE
    ${OpenCV_INCLUDE_DIRS}
    ${cnpy_SOURCE_DIR}
)

target_link_libraries(stereo_rectify
    ${OpenCV_LIBS}
    cnpy
    z   # zlib, required by cnpy
)
