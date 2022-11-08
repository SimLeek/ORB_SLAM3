cmake_minimum_required(VERSION 3.12)

set(CMAKE_TOOLCHAIN_FILE "C:/Users/joshm/code/vcpkg/scripts/buildsystems/vcpkg.cmake")
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

find_package(Pangolin REQUIRED)
find_package(DBoW2 REQUIRED)
find_package(DLib REQUIRED)
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
        ${DBoW2_LIBS}
        ${DLib_LIBRARIES}
        ${Pangolin_LIBRARIES}
)

add_executable(dbow2_builder
        dbow2_builder.cc)
target_link_libraries(dbow2_builder ${LINK_LIBS})

if(realsense2_FOUND)
    include_directories(${PROJECT_NAME}
    ${realsense_INCLUDE_DIR}
    )

    add_executable(recorder_realsense_T265
        recorder_realsense_T265.cc)
    target_link_libraries(recorder_realsense_T265 ${LINK_LIBS} ${realsense2_LIBRARY})

    add_executable(recorder_realsense_D435i
        recorder_realsense_D435i.cc)
    target_link_libraries(recorder_realsense_D435i ${LINK_LIBS} ${realsense2_LIBRARY})
endif()
