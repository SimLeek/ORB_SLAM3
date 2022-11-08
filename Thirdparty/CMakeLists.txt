cmake_minimum_required( VERSION 3.7.0 )

#set(CMAKE_TOOLCHAIN_FILE "C:/Users/?/code/vcpkg/scripts/buildsystems/vcpkg.cmake")

project( Thirdparty )

find_package(Git)
if(NOT GIT_FOUND)
  message(ERROR "Cannot find git. git is required for building the third party libraries")
endif()

include( ExternalProject )

list(APPEND CMAKE_PREFIX_PATH "${CMAKE_BINARY_DIR}/build/thirdparty")
list(APPEND CMAKE_PREFIX_PATH "${CMAKE_BINARY_DIR}/build/thirdparty/x64/vc16/")
list(APPEND CMAKE_PREFIX_PATH "${CMAKE_BINARY_DIR}/build/thirdparty/x64/vc16/lib/")

#set(INSTALL_STEP "1" CACHE STRING "Which install step are we on?")
set(INSTALL_STEP "2" CACHE STRING "Which install step are we on?")

set($ENV{EIGEN3_ROOT_DIR} "${CMAKE_BINARY_DIR}/build/thirdparty")


if("${INSTALL_STEP}" EQUAL "1")
#externalproject_add(
#    Eigen3 
#    GIT_REPOSITORY "https://gitlab.com/libeigen/eigen.git"
#    GIT_TAG "3.4.0"
#    SOURCE_DIR eigan3
#    BINARY_DIR eigan3-build
#    INSTALL_DIR eigan3-install
#    CMAKE_ARGS
#      -DBUILD_DOCS:BOOL=OFF
#      -DEIGEN_BUILD_DOC:BOOL=OFF
#      -DBUILD_EXAMPLES:BOOL=OFF
#      -DEIGEN_BUILD_TESTING=OFF
#      -DBUILD_TESTING:BOOL=OFF
#      -DCMAKE_INSTALL_PREFIX:PATH=${CMAKE_BINARY_DIR}/thirdparty
#)

IF (WIN32)
  find_package(Pangolin CONFIG REQUIRED)
  find_package(OpenCV CONFIG REQUIRED)

ELSE (WIN32)
externalproject_add(
    pangolin 
    GIT_REPOSITORY "https://github.com/stevenlovegrove/Pangolin.git"
    GIT_TAG "v0.7"
    SOURCE_DIR pangolin
    BINARY_DIR pangolin-build
    INSTALL_DIR pangolin-install
    CMAKE_ARGS
      -DBUILD_SHARED_LIBS:BOOL=ON
      -DBUILD_EXAMPLES:BOOL=OFF
      -DBUILD_TESTS:BOOL=OFF
      -DCMAKE_INSTALL_PREFIX:PATH=${CMAKE_BINARY_DIR}/thirdparty
)
ENDIF (WIN32)

# note: imported_implib problems
# download and extract OpenCV from github.
# todo: make this build in the first run, and seperate libs by interdependencies
#externalproject_add(
#    opencv 
#    GIT_REPOSITORY "https://github.com/opencv/opencv.git"
#    GIT_TAG "4.6.0"
#    SOURCE_DIR opencv
#    BINARY_DIR opencv-build
#    INSTALL_DIR opencv-install
#    CMAKE_ARGS
#      -DBUILD_DOCS:BOOL=OFF
#      -DBUILD_EXAMPLES:BOOL=OFF
#      -DBUILD_WITH_DEBUG_INFO=OFF
#      -DBUILD_opencv_core=ON
#      -DBUILD_opencv_imgproc=ON
#      -DBUILD_opencv_highgui=ON
#      -DBUILD_opencv_video=ON
#      -DBUILD_opencv_flann=ON
#      -DBUILD_opencv_ml=ON
#      -DBUILD_opencv_features2d=ON
#      -DBUILD_opencv_photo=ON
#      -DBUILD_opencv_calib3d=ON
#      -DBUILD_opencv_features2d=ON
#      -DBUILD_opencv_stitching=ON
#      -DBUILD_opencv_dnn=ON
#      -DBUILD_opencv_objdetect=ON
#      -DBUILD_opencv_apps=OFF
#      -DBUILD_opencv_gpu=ON
#      -DBUILD_SHARED_LIBS:BOOL=ON
#      -DBUILD_TESTS:BOOL=OFF
#      -DBUILD_PERF_TESTS:BOOL=OFF
#      -DBUILD_opencv_contrib=ON
#      -DCMAKE_BUILD_TYPE:STRING=Release
#      -DWITH_FFMPEG:BOOL=ON
#      -DWITH_WITH_PROTOBUF:BOOL=ON
#      -DBUILD_opencv_python3:BOOL=ON
#      -DWITH_WITH_PROTOBUF:BOOL=ON
#      -DBUILD_PNG:BOOL=ON
#      -DBUILD_JPEG:BOOL=ON
#      -DBUILD_ZLIB:BOOL=ON
#      -DCMAKE_INSTALL_PREFIX:PATH=${CMAKE_BINARY_DIR}/thirdparty
#)

# luckily, someone already updated it to the latest opencv for me. :3
#externalproject_add(
#    DLib  
#    GIT_REPOSITORY "https://github.com/kerolex/DLib.git"
#    GIT_TAG "335311a16f788f283e2f9a4cd2b6dec9dd5bf5b7"
#    SOURCE_DIR DLib
#    BINARY_DIR DLib-build
#    INSTALL_DIR DLib-install
#    CMAKE_ARGS
#      -DCMAKE_INSTALL_PREFIX:PATH=${CMAKE_BINARY_DIR}/thirdparty
#      -DCMAKE_TOOLCHAIN_FILE:string=${CMAKE_TOOLCHAIN_FILE}
#      )

#externalproject_add(
#    FMT   
#    GIT_REPOSITORY "https://github.com/fmtlib/fmt.git"
#    GIT_TAG "5.3.0"
#    SOURCE_DIR FMT
#    BINARY_DIR FMT-build
#    INSTALL_DIR FMT-install
#    CMAKE_ARGS
#      -DCMAKE_INSTALL_PREFIX:PATH=${CMAKE_BINARY_DIR}/thirdparty
#)
elseif("${INSTALL_STEP}" EQUAL "2")
# this fork has a fix for a loading issue that makes decent sized databases take up to a year to load.
# 3 minutes of loading for 300000 entries, index is ~O(n/2), 150000*5 minutes~= 1.5 years
externalproject_add(
    DBoW2  
    GIT_REPOSITORY "https://github.com/IronSublimate/DBoW2.git"
    GIT_TAG b1657991c49a5c76a5c1571e98563bb9b0ade647
    SOURCE_DIR DBoW2
    BINARY_DIR DBoW2-build
    INSTALL_DIR DBoW2-install
    CMAKE_ARGS
      -DBUILD_Demo:BOOL=OFF
      -DBUILD_DBoW2:BOOL=ON
      -DCMAKE_INSTALL_PREFIX:PATH=${CMAKE_BINARY_DIR}/thirdparty
)

# note: to get sophus working, I had to add this to its FindEigan3.cmake file:
#  set(EIGEN3_INCLUDE_DIR "${CMAKE_BINARY_DIR}/../thirdparty/include/eigen3")

#externalproject_add(
#    Sophus  
#    GIT_REPOSITORY "https://github.com/strasdat/Sophus.git"
#    GIT_TAG "v22.10"
#    SOURCE_DIR Sophus
#    BINARY_DIR Sophus-build
#    INSTALL_DIR Sophus-install
#    CMAKE_ARGS
#      -DBUILD_SOPHUS_TESTS:BOOL=OFF
#      -DBUILD_SOPHUS_EXAMPLES:BOOL=OFF
#      -DCMAKE_INSTALL_PREFIX:PATH=${CMAKE_BINARY_DIR}/thirdparty
#)

#externalproject_add(
#    librealsense2  
#    GIT_REPOSITORY "https://github.com/IntelRealSense/librealsense.git"
#    GIT_TAG "v2.51.1"
#    SOURCE_DIR librealsense2
#    BINARY_DIR librealsense2-build
#    INSTALL_DIR librealsense2-install
#    CMAKE_ARGS
#      -DBUILD_SHARED_LIBS:BOOL=ON
#      -DBUILD_EXAMPLES:BOOL=OFF
#      -DBUILD_TESTS:BOOL=OFF
#      -DCPP11_NO_BOOST:BOOL=ON
#      -DCMAKE_INSTALL_PREFIX:PATH=${CMAKE_BINARY_DIR}/thirdparty
#)



#externalproject_add(
#    g2o  
#    GIT_REPOSITORY "https://github.com/RainerKuemmerle/g2o.git"
#    GIT_TAG "20201223_git"
#    SOURCE_DIR g2o
#    BINARY_DIR g2o-build
#    INSTALL_DIR g2o-install
#    CMAKE_ARGS
#      -DG2O_FAST_MATH:BOOL=ON
#      -DBUILD_SHARED_LIBS:BOOL=ON
#      -DG2O_BUILD_EXAMPLES:BOOL=OFF
#      -DG2O_BUILD_APPS:BOOL=OFF
#      -DCMAKE_INSTALL_PREFIX:PATH=${CMAKE_BINARY_DIR}/thirdparty
#)

endif()
#set(GLEW_INCLUDE_DIR, "/glew-2.0.0/include/")
#set(GLEW_LIBRARY, "/glew-2.0.0/lib")

#set(GLEW_INCLUDE_DIR "${CMAKE_BINARY_DIR}/thirdparty/include/")
#set(GLEW_LIBRARY "${CMAKE_BINARY_DIR}/thirdparty/x64/vc16/lib/")
#SET( GLEW_FOUND TRUE )











