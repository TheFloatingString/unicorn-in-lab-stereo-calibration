cmake_minimum_required(VERSION 3.16)
project(stereo_rectify CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ---- OpenCV (local extraction from opencv-4.13.0-windows.exe) ----
# Run the .exe once to extract — it creates an opencv/ folder next to it.
# The CMake config lives at opencv/build/
if(NOT OpenCV_DIR)
    set(_local_opencv "${CMAKE_SOURCE_DIR}/opencv/build")
    if(EXISTS "${_local_opencv}/OpenCVConfig.cmake")
        set(OpenCV_DIR "${_local_opencv}" CACHE PATH "Local OpenCV build dir" FORCE)
    endif()
endif()
find_package(OpenCV REQUIRED COMPONENTS core imgproc highgui imgcodecs)

include(FetchContent)

# ---- zlib (fetched from source — no vcpkg or system install needed) ----
FetchContent_Declare(
    zlib
    GIT_REPOSITORY https://github.com/madler/zlib.git
    GIT_TAG        v1.3.1
)
FetchContent_MakeAvailable(zlib)
if(NOT TARGET ZLIB::ZLIB)
    add_library(ZLIB::ZLIB ALIAS zlibstatic)
endif()

# ---- cnpy (compiled directly to skip its internal find_package(ZLIB)) ----
# cnpy is a single .cpp file so we compile it ourselves instead of using
# its CMakeLists.txt, which would re-run find_package(ZLIB) against the system.
FetchContent_Declare(
    cnpy
    GIT_REPOSITORY https://github.com/rogersce/cnpy.git
    GIT_TAG        master
)
FetchContent_GetProperties(cnpy)
if(NOT cnpy_POPULATED)
    FetchContent_Populate(cnpy)
endif()
add_library(cnpy STATIC ${cnpy_SOURCE_DIR}/cnpy.cpp)
target_include_directories(cnpy PUBLIC ${cnpy_SOURCE_DIR})
target_link_libraries(cnpy PUBLIC ZLIB::ZLIB)

# ---- Main executable ----
add_executable(stereo_rectify main.cpp)
target_include_directories(stereo_rectify PRIVATE ${OpenCV_INCLUDE_DIRS})
target_link_libraries(stereo_rectify
    ${OpenCV_LIBS}
    cnpy
)

# Copy OpenCV DLLs next to the exe so it runs without modifying PATH
add_custom_command(TARGET stereo_rectify POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        $<TARGET_RUNTIME_DLLS:stereo_rectify>
        $<TARGET_FILE_DIR:stereo_rectify>
    COMMAND_EXPAND_LISTS
)
