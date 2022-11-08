cmake_minimum_required(VERSION 3.12)

# set(CMAKE_TOOLCHAIN_FILE "C:/Users/?/code/vcpkg/scripts/buildsystems/vcpkg.cmake")
set(CMAKE_GENERATOR_PLATFORM x64)

project(MONOCULAR_ORB_SLAM3)

set (CMAKE_CXX_STANDARD 17)  # result_of is removed in c++20, so fmt won't compile.
if(MSVC)
add_compile_options(/std:c++17)
message("added c++17 option msvc")
        if((MSVC_VERSION GREATER_EQUAL 1914))
        add_compile_options(/Zc:__cplusplus)
        message("added /Zc:__cplusplus option msvc")
        endif()
# set stack reserved size to ~10MB
# CMake previously automatically set this value for MSVC builds, but the
# behavior was changed in CMake 2.8.11 (Issue 12437) to use the MSVC default
# value (1 MB) which is not enough for us in tasks such as parsing recursive
# C++ templates in Clang.
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} /STACK:10000000")
endif(MSVC)

message("PROJECT_SOURCE_DIR")
message("${PROJECT_SOURCE_DIR}")

list(APPEND CMAKE_PREFIX_PATH "${PROJECT_SOURCE_DIR}/../../Thirdparty/build/thirdparty")
list(APPEND CMAKE_PREFIX_PATH "${PROJECT_SOURCE_DIR}/../../Thirdparty/build/thirdparty/x64/vc16")
list(APPEND CMAKE_PREFIX_PATH "${PROJECT_SOURCE_DIR}/../../Thirdparty/build/thirdparty/x64/vc16/bin")
list(APPEND CMAKE_PREFIX_PATH "${PROJECT_SOURCE_DIR}/../../Thirdparty/build/thirdparty/x64/vc16/lib")

set (CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/../../Thirdparty/build/thirdparty/lib/cmake")

link_directories("${PROJECT_SOURCE_DIR}/../../Thirdparty/build/thirdparty")
link_directories("${PROJECT_SOURCE_DIR}/../../Thirdparty/build/thirdparty/x64/vc16")
link_directories("${PROJECT_SOURCE_DIR}/../../Thirdparty/build/thirdparty/x64/vc16/bin")
link_directories("${PROJECT_SOURCE_DIR}/../../Thirdparty/build/thirdparty/x64/vc16/lib")

link_directories("${PROJECT_SOURCE_DIR}/../../build/lib")  # self reference outputted libs from previous steps
link_directories("${PROJECT_SOURCE_DIR}/../../build/bin")  # self reference outputted libs from previous steps
list(APPEND CMAKE_PREFIX_PATH "${PROJECT_SOURCE_DIR}/../../build/lib")
list(APPEND CMAKE_PREFIX_PATH "${PROJECT_SOURCE_DIR}/../../build/bin")

set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/lib)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/bin)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/bin)

LIST(APPEND CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake_modules)

find_package(OpenCV 4.4)
   if(NOT OpenCV_FOUND)
      message(FATAL_ERROR "OpenCV > 4.4 not found.")
   endif()
MESSAGE("OPENCV VERSION:")
MESSAGE(${OpenCV_VERSION})

find_package(Boost REQUIRED filesystem)
find_package(Pangolin REQUIRED)
find_package(DBoW2 REQUIRED)
find_package(realsense2)


include_directories(
${PROJECT_SOURCE_DIR}/../..
${PROJECT_SOURCE_DIR}/../../include
${PROJECT_SOURCE_DIR}/../../include/CameraModels
${PROJECT_SOURCE_DIR}/../../Thirdparty/build/Sophus
${PROJECT_SOURCE_DIR}/../../Thirdparty/build/thirdparty/include
${EIGEN3_INCLUDE_DIR}
${Pangolin_INCLUDE_DIRS}
)

set(SLAM_LIB ORB_SLAM3)

set(LINK_LIBS
        ${SLAM_LIB}
        ${OpenCV_LIBS}
        ${Pangolin_LIBRARIES}
        ${Boost_LIBRARIES}
)

add_executable(mono_cam2
        mono_cam.cc)
target_link_libraries(mono_cam2 ${LINK_LIBS})

add_executable(mono_tum
        mono_tum.cc)
target_link_libraries(mono_tum ${LINK_LIBS})

add_executable(mono_kitti
        mono_kitti.cc)
target_link_libraries(mono_kitti ${LINK_LIBS})

add_executable(mono_euroc
        mono_euroc.cc)
target_link_libraries(mono_euroc ${LINK_LIBS})

add_executable(mono_tum_vi
        mono_tum_vi.cc)
target_link_libraries(mono_tum_vi ${LINK_LIBS})

if(realsense2_FOUND)
    include_directories(${PROJECT_NAME}
    ${realsense_INCLUDE_DIR}
    )

    add_executable(mono_realsense_t265
            mono_realsense_t265.cc)
    target_link_libraries(mono_realsense_t265 ${LINK_LIBS} ${realsense2_LIBRARY})

    add_executable(mono_realsense_D435i
            mono_realsense_D435i.cc)
    target_link_libraries(mono_realsense_D435i ${LINK_LIBS} ${realsense2_LIBRARY})
endif()
