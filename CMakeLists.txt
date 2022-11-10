cmake_minimum_required(VERSION 3.12)

#set(CMAKE_TOOLCHAIN_FILE "C:/Users/?/code/vcpkg/scripts/buildsystems/vcpkg.cmake")
set(CMAKE_GENERATOR_PLATFORM x64)


project(ORB_SLAM3)

include(GenerateExportHeader)

if(MSVC)
  add_compile_options(/bigobj)
  add_compile_options(/Zc:__cplusplus) # required to compile fmt correctly since it uses this to determine between new and deprecated code
  add_compile_options(/Zi) # edit and continue option. Instead of waiting an hour for this large project to re-compile.
else ()
  add_compile_options(-Wa -mbig-obj)
endif ()

set (CMAKE_CXX_STANDARD 17) # 17 is the max standard we can use while still importing fmt, because fmt uses std::result_of, which is removed in c++20

IF(NOT CMAKE_BUILD_TYPE)
  SET(CMAKE_BUILD_TYPE Release)
ENDIF()

#list(APPEND CMAKE_PREFIX_PATH "${CMAKE_BINARY_DIR}/Thirdparty/thirdparty")
#list(APPEND CMAKE_PREFIX_PATH "${CMAKE_BINARY_DIR}/Thirdparty/thirdparty/x64/vc16")
#list(APPEND CMAKE_PREFIX_PATH "${CMAKE_BINARY_DIR}/Thirdparty/thirdparty/x64/vc16/bin")
#list(APPEND CMAKE_PREFIX_PATH "${CMAKE_BINARY_DIR}/Thirdparty/thirdparty/x64/vc16/lib")
#message("bin dir:")
#message(${CMAKE_BINARY_DIR})

list(APPEND CMAKE_PREFIX_PATH "${CMAKE_BINARY_DIR}/../Thirdparty/build/thirdparty")
list(APPEND CMAKE_PREFIX_PATH "${CMAKE_BINARY_DIR}/../Thirdparty/build/thirdparty/x64/vc16")
list(APPEND CMAKE_PREFIX_PATH "${CMAKE_BINARY_DIR}/../Thirdparty/build/thirdparty/x64/vc16/bin")
list(APPEND CMAKE_PREFIX_PATH "${CMAKE_BINARY_DIR}/../Thirdparty/build/thirdparty/x64/vc16/lib")

set (CMAKE_MODULE_PATH "${CMAKE_BINARY_DIR}/../Thirdparty/build/thirdparty/lib/cmake")

link_directories("${CMAKE_BINARY_DIR}/../Thirdparty/build/thirdparty")
link_directories("${CMAKE_BINARY_DIR}/../Thirdparty/build/thirdparty/x64/vc16")
link_directories("${CMAKE_BINARY_DIR}/../Thirdparty/build/thirdparty/x64/vc16/bin")
link_directories("${CMAKE_BINARY_DIR}/../Thirdparty/build/thirdparty/x64/vc16/lib")

link_directories("${CMAKE_CURRENT_BINARY_DIR}/lib")  # self reference outputted libs from previous steps
link_directories("${CMAKE_CURRENT_BINARY_DIR}/bin")  # self reference outputted libs from previous steps
list(APPEND CMAKE_PREFIX_PATH "${CMAKE_CURRENT_BINARY_DIR}/lib")
list(APPEND CMAKE_PREFIX_PATH "${CMAKE_CURRENT_BINARY_DIR}/bin")

MESSAGE("Build type: " ${CMAKE_BUILD_TYPE})


if(MSVC)
#if (CMAKE_BUILD_TYPE STREQUAL "Release" OR CMAKE_BUILD_TYPE STREQUAL "MinSizeRel")
  set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS}  -Wall   -O1") # was 0x, but that leads to weird stackoverflow errors
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall   -O1")
#else()
#  set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS}  -Wall   -Ox") # was 0x, but that leads to weird stackoverflow errors
#  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall   -Ox")
#endif()
# set stack reserved size to ~10MB
# CMake previously automatically set this value for MSVC builds, but the
# behavior was changed in CMake 2.8.11 (Issue 12437) to use the MSVC default
# value (1 MB) which is not enough for us in tasks such as parsing recursive
# C++ templates in Clang.
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} /STACK:10000000")
else ()


        set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS}  -Wall   -O3")
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall   -O3")
endif ()

set(CMAKE_C_FLAGS_RELEASE "${CMAKE_C_FLAGS_RELEASE} -march=native")
set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -march=native")

LIST(APPEND CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake_modules)

find_package(OpenCV 4.4)
   if(NOT OpenCV_FOUND)
      message(FATAL_ERROR "OpenCV > 4.4 not found.")
   endif()

MESSAGE("OPENCV VERSION:")
MESSAGE(${OpenCV_VERSION})

find_package(Eigen3 3.1.0 REQUIRED)
find_package(Pangolin REQUIRED)
find_package(realsense2)

include_directories(
${PROJECT_SOURCE_DIR}
${PROJECT_SOURCE_DIR}/include
${PROJECT_SOURCE_DIR}/include/CameraModels
${PROJECT_SOURCE_DIR}/Thirdparty/build/Sophus
${EIGEN3_INCLUDE_DIR}
${Pangolin_INCLUDE_DIRS}
)

set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/lib)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/bin)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/bin)

add_library(${PROJECT_NAME} SHARED
src/System.cc
src/Tracking.cc
src/LocalMapping.cc
src/LoopClosing.cc
src/ORBextractor.cc
src/ORBmatcher.cc
src/FrameDrawer.cc
src/Converter.cc
src/MapPoint.cc
src/KeyFrame.cc
src/Atlas.cc
src/Map.cc
src/MapDrawer.cc
src/Optimizer.cc
src/Frame.cc
src/KeyFrameDatabase.cc
src/Sim3Solver.cc
src/Viewer.cc
src/ImuTypes.cc
src/G2oTypes.cc
src/CameraModels/Pinhole.cpp
src/CameraModels/KannalaBrandt8.cpp
src/OptimizableTypes.cpp
src/MLPnPsolver.cpp
src/GeometricTools.cc
src/TwoViewReconstruction.cc
src/Config.cc
src/Settings.cc
include/System.h
include/Tracking.h
include/LocalMapping.h
include/LoopClosing.h
include/ORBextractor.h
include/ORBmatcher.h
include/FrameDrawer.h
include/Converter.h
include/MapPoint.h
include/KeyFrame.h
include/Atlas.h
include/Map.h
include/MapDrawer.h
include/Optimizer.h
include/Frame.h
include/KeyFrameDatabase.h
include/Sim3Solver.h
include/Viewer.h
include/ImuTypes.h
include/G2oTypes.h
include/CameraModels/GeometricCamera.h
include/CameraModels/Pinhole.h
include/CameraModels/KannalaBrandt8.h
include/OptimizableTypes.h
include/MLPnPsolver.h
include/MultiPlatform.h
include/GeometricTools.h
include/TwoViewReconstruction.h
include/SerializationUtils.h
include/Config.h
include/Settings.h)

generate_export_header(${PROJECT_NAME})

if ( MSVC )
    set_target_properties( ${PROJECT_NAME} PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${CMAKE_LIBRARY_OUTPUT_DIRECTORY} )
    set_target_properties( ${PROJECT_NAME} PROPERTIES LIBRARY_OUTPUT_DIRECTORY_DEBUG ${CMAKE_LIBRARY_OUTPUT_DIRECTORY} )
    set_target_properties( ${PROJECT_NAME} PROPERTIES LIBRARY_OUTPUT_DIRECTORY_RELEASE ${CMAKE_LIBRARY_OUTPUT_DIRECTORY} )
    set_target_properties( ${PROJECT_NAME} PROPERTIES ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_ARCHIVE_OUTPUT_DIRECTORY} )
    set_target_properties( ${PROJECT_NAME} PROPERTIES ARCHIVE_OUTPUT_DIRECTORY_DEBUG ${CMAKE_ARCHIVE_OUTPUT_DIRECTORY} )
    set_target_properties( ${PROJECT_NAME} PROPERTIES ARCHIVE_OUTPUT_DIRECTORY_RELEASE ${CMAKE_ARCHIVE_OUTPUT_DIRECTORY} )
    set_target_properties( ${PROJECT_NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${CMAKE_RUNTIME_OUTPUT_DIRECTORY} )
    set_target_properties( ${PROJECT_NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY_DEBUG ${CMAKE_RUNTIME_OUTPUT_DIRECTORY} )
    set_target_properties( ${PROJECT_NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY_RELEASE ${CMAKE_RUNTIME_OUTPUT_DIRECTORY} )
    # etc for the other available configuration types (MinSizeRel, RelWithDebInfo)
endif ( MSVC )

#add_subdirectory(Thirdparty/build/g2o)

find_package(Boost REQUIRED serialization)
find_package(OpenSSL REQUIRED)
find_package(g2o REQUIRED)
find_package(DBoW2 REQUIRED)
# Was literally just needed for the randint function... wtf.
#find_package(DLib REQUIRED)
find_package(fmt REQUIRED)

#message("DLIB LIBS:")
#message("${DLib_LIBRARIES}")


target_link_libraries(${PROJECT_NAME}
${OpenCV_LIBS}
${EIGEN3_LIBS}
${Pangolin_LIBRARIES}
${DBoW2_LIBRARIES}
g2o::stuff
g2o::opengl_helper
g2o::core
g2o::types_data
g2o::types_slam2d
g2o::types_slam3d
g2o::types_sba
g2o::types_sim3
g2o::types_icp
g2o::types_sclam2d
g2o::types_slam2d_addons
g2o::types_slam3d_addons
g2o::solver_pcg
g2o::solver_dense
g2o::solver_structure_only
g2o::solver_eigen
fmt::fmt
${Boost_LIBRARIES}
OpenSSL::Crypto
)

target_compile_definitions(${PROJECT_NAME} PUBLIC -DCOMPILING_DLL -DCOMPILEDWITHC11)

# If RealSense SDK is found the library is added and its examples compiled
if(realsense2_FOUND)
    include_directories(${PROJECT_NAME}
    ${realsense_INCLUDE_DIR}
    )
    target_link_libraries(${PROJECT_NAME}
    ${realsense2_LIBRARY}
    )
endif()


# Build examples

# RGB-D examples
#set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/Examples/RGB-D)
#
#add_executable(rgbd_tum
#        Examples/RGB-D/rgbd_tum.cc)
#target_link_libraries(rgbd_tum ${PROJECT_NAME})
#
#if(realsense2_FOUND)
#    add_executable(rgbd_realsense_D435i
#            Examples/RGB-D/rgbd_realsense_D435i.cc)
#    target_link_libraries(rgbd_realsense_D435i ${PROJECT_NAME})
#endif()
#
#
## RGB-D inertial examples
#set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/Examples/RGB-D-Inertial)
#
#if(realsense2_FOUND)
#    add_executable(rgbd_inertial_realsense_D435i
#            Examples/RGB-D-Inertial/rgbd_inertial_realsense_D435i.cc)
#    target_link_libraries(rgbd_inertial_realsense_D435i ${PROJECT_NAME})
#endif()
#
##Stereo examples
#set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/Examples/Stereo)
#
#add_executable(stereo_kitti
#        Examples/Stereo/stereo_kitti.cc)
#target_link_libraries(stereo_kitti ${PROJECT_NAME})
#
#add_executable(stereo_euroc
#        Examples/Stereo/stereo_euroc.cc)
#target_link_libraries(stereo_euroc ${PROJECT_NAME})
#
#add_executable(stereo_tum_vi
#        Examples/Stereo/stereo_tum_vi.cc)
#target_link_libraries(stereo_tum_vi ${PROJECT_NAME})
#
#if(realsense2_FOUND)
#    add_executable(stereo_realsense_t265
#            Examples/Stereo/stereo_realsense_t265.cc)
#    target_link_libraries(stereo_realsense_t265 ${PROJECT_NAME})
#
#    add_executable(stereo_realsense_D435i
#            Examples/Stereo/stereo_realsense_D435i.cc)
#    target_link_libraries(stereo_realsense_D435i ${PROJECT_NAME})
#endif()
#
##Monocular examples
#set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/Examples/Monocular)
#
#add_executable(mono_tum
#        Examples/Monocular/mono_tum.cc)
#target_link_libraries(mono_tum ${PROJECT_NAME})
#
#add_executable(mono_kitti
#        Examples/Monocular/mono_kitti.cc)
#target_link_libraries(mono_kitti ${PROJECT_NAME})
#
#add_executable(mono_euroc
#        Examples/Monocular/mono_euroc.cc)
#target_link_libraries(mono_euroc ${PROJECT_NAME})
#
#add_executable(mono_tum_vi
#        Examples/Monocular/mono_tum_vi.cc)
#target_link_libraries(mono_tum_vi ${PROJECT_NAME})
#
#if(realsense2_FOUND)
#    add_executable(mono_realsense_t265
#            Examples/Monocular/mono_realsense_t265.cc)
#    target_link_libraries(mono_realsense_t265 ${PROJECT_NAME})
#
#    add_executable(mono_realsense_D435i
#            Examples/Monocular/mono_realsense_D435i.cc)
#    target_link_libraries(mono_realsense_D435i ${PROJECT_NAME})
#endif()
#
##Monocular inertial examples
#set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/Examples/Monocular-Inertial)
#
#add_executable(mono_inertial_euroc
#        Examples/Monocular-Inertial/mono_inertial_euroc.cc)
#target_link_libraries(mono_inertial_euroc ${PROJECT_NAME})
#
#add_executable(mono_inertial_tum_vi
#        Examples/Monocular-Inertial/mono_inertial_tum_vi.cc)
#target_link_libraries(mono_inertial_tum_vi ${PROJECT_NAME})
#
#if(realsense2_FOUND)
#    add_executable(mono_inertial_realsense_t265
#            Examples/Monocular-Inertial/mono_inertial_realsense_t265.cc)
#    target_link_libraries(mono_inertial_realsense_t265 ${PROJECT_NAME})
#
#    add_executable(mono_inertial_realsense_D435i
#            Examples/Monocular-Inertial/mono_inertial_realsense_D435i.cc)
#    target_link_libraries(mono_inertial_realsense_D435i ${PROJECT_NAME})
#endif()
#
##Stereo Inertial examples
#set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/Examples/Stereo-Inertial)
#
#add_executable(stereo_inertial_euroc
#        Examples/Stereo-Inertial/stereo_inertial_euroc.cc)
#target_link_libraries(stereo_inertial_euroc ${PROJECT_NAME})
#
#add_executable(stereo_inertial_tum_vi
#        Examples/Stereo-Inertial/stereo_inertial_tum_vi.cc)
#target_link_libraries(stereo_inertial_tum_vi ${PROJECT_NAME})
#
#if(realsense2_FOUND)
#    add_executable(stereo_inertial_realsense_t265
#            Examples/Stereo-Inertial/stereo_inertial_realsense_t265.cc)
#    target_link_libraries(stereo_inertial_realsense_t265 ${PROJECT_NAME})
#
#    add_executable(stereo_inertial_realsense_D435i
#            Examples/Stereo-Inertial/stereo_inertial_realsense_D435i.cc)
#    target_link_libraries(stereo_inertial_realsense_D435i ${PROJECT_NAME})
#endif()
#
#set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/Examples/Calibration)
#if(realsense2_FOUND)
#    add_executable(recorder_realsense_D435i
#            Examples/Calibration/recorder_realsense_D435i.cc)
#    target_link_libraries(recorder_realsense_D435i ${PROJECT_NAME})
#
#    add_executable(recorder_realsense_T265
#            Examples/Calibration/recorder_realsense_T265.cc)
#    target_link_libraries(recorder_realsense_T265 ${PROJECT_NAME})
#endif()
#
##Old examples
#
## RGB-D examples
#set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/Examples_old/RGB-D)
#
#add_executable(rgbd_tum_old
#        Examples_old/RGB-D/rgbd_tum.cc)
#target_link_libraries(rgbd_tum_old ${PROJECT_NAME})
#
#if(realsense2_FOUND)
#    add_executable(rgbd_realsense_D435i_old
#            Examples_old/RGB-D/rgbd_realsense_D435i.cc)
#    target_link_libraries(rgbd_realsense_D435i_old ${PROJECT_NAME})
#endif()
#
#
## RGB-D inertial examples
#set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/Examples_old/RGB-D-Inertial)
#
#if(realsense2_FOUND)
#    add_executable(rgbd_inertial_realsense_D435i_old
#            Examples_old/RGB-D-Inertial/rgbd_inertial_realsense_D435i.cc)
#    target_link_libraries(rgbd_inertial_realsense_D435i_old ${PROJECT_NAME})
#endif()
#
##Stereo examples
#set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/Examples_old/Stereo)
#
#add_executable(stereo_kitti_old
#        Examples_old/Stereo/stereo_kitti.cc)
#target_link_libraries(stereo_kitti_old ${PROJECT_NAME})
#
#add_executable(stereo_euroc_old
#        Examples_old/Stereo/stereo_euroc.cc)
#target_link_libraries(stereo_euroc_old ${PROJECT_NAME})
#
#add_executable(stereo_tum_vi_old
#        Examples_old/Stereo/stereo_tum_vi.cc)
#target_link_libraries(stereo_tum_vi_old ${PROJECT_NAME})
#
#if(realsense2_FOUND)
#    add_executable(stereo_realsense_t265_old
#            Examples_old/Stereo/stereo_realsense_t265.cc)
#    target_link_libraries(stereo_realsense_t265_old ${PROJECT_NAME})
#
#    add_executable(stereo_realsense_D435i_old
#            Examples_old/Stereo/stereo_realsense_D435i.cc)
#    target_link_libraries(stereo_realsense_D435i_old ${PROJECT_NAME})
#endif()
#
##Monocular examples
#set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/Examples_old/Monocular)
#
#add_executable(mono_tum_old
#        Examples_old/Monocular/mono_tum.cc)
#target_link_libraries(mono_tum_old ${PROJECT_NAME})
#
#add_executable(mono_kitti_old
#        Examples_old/Monocular/mono_kitti.cc)
#target_link_libraries(mono_kitti_old ${PROJECT_NAME})
#
#add_executable(mono_euroc_old
#        Examples_old/Monocular/mono_euroc.cc)
#target_link_libraries(mono_euroc_old ${PROJECT_NAME})
#
#add_executable(mono_tum_vi_old
#        Examples_old/Monocular/mono_tum_vi.cc)
#target_link_libraries(mono_tum_vi_old ${PROJECT_NAME})
#
#if(realsense2_FOUND)
#    add_executable(mono_realsense_t265_old
#            Examples_old/Monocular/mono_realsense_t265.cc)
#    target_link_libraries(mono_realsense_t265_old ${PROJECT_NAME})
#
#    add_executable(mono_realsense_D435i_old
#            Examples_old/Monocular/mono_realsense_D435i.cc)
#    target_link_libraries(mono_realsense_D435i_old ${PROJECT_NAME})
#endif()
#
##Monocular inertial examples
#set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/Examples_old/Monocular-Inertial)
#
#add_executable(mono_inertial_euroc_old
#        Examples_old/Monocular-Inertial/mono_inertial_euroc.cc)
#target_link_libraries(mono_inertial_euroc_old ${PROJECT_NAME})
#
#add_executable(mono_inertial_tum_vi_old
#        Examples_old/Monocular-Inertial/mono_inertial_tum_vi.cc)
#target_link_libraries(mono_inertial_tum_vi_old ${PROJECT_NAME})
#
#if(realsense2_FOUND)
#    add_executable(mono_inertial_realsense_t265_old
#            Examples_old/Monocular-Inertial/mono_inertial_realsense_t265.cc)
#    target_link_libraries(mono_inertial_realsense_t265_old ${PROJECT_NAME})
#
#    add_executable(mono_inertial_realsense_D435i_old
#            Examples_old/Monocular-Inertial/mono_inertial_realsense_D435i.cc)
#    target_link_libraries(mono_inertial_realsense_D435i_old ${PROJECT_NAME})
#endif()
#
##Stereo Inertial examples
#set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/Examples_old/Stereo-Inertial)
#
#add_executable(stereo_inertial_euroc_old
#        Examples_old/Stereo-Inertial/stereo_inertial_euroc.cc)
#target_link_libraries(stereo_inertial_euroc_old ${PROJECT_NAME})
#
#add_executable(stereo_inertial_tum_vi_old
#        Examples_old/Stereo-Inertial/stereo_inertial_tum_vi.cc)
#target_link_libraries(stereo_inertial_tum_vi_old ${PROJECT_NAME})
#
#if(realsense2_FOUND)
#    add_executable(stereo_inertial_realsense_t265_old
#            Examples_old/Stereo-Inertial/stereo_inertial_realsense_t265.cc)
#    target_link_libraries(stereo_inertial_realsense_t265_old ${PROJECT_NAME})
#
#    add_executable(stereo_inertial_realsense_D435i_old
#            Examples_old/Stereo-Inertial/stereo_inertial_realsense_D435i.cc)
#    target_link_libraries(stereo_inertial_realsense_D435i_old ${PROJECT_NAME})
#endif()
#