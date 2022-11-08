@echo off

WHERE cmake
IF %ERRORLEVEL% NEQ 0 (
    ECHO cmake wasn't found 
    EXIT /B -1
)


IF NOT EXIST "C:\Program Files\7-Zip\7z.exe" (
    ECHO 7z wasn't found 
    EXIT /B -1
)

echo "Configuring and building Thirdparty/DBoW2 ..."

cd Thirdparty/DBoW2
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build . -j

cd ../../g2o

echo "Configuring and building Thirdparty/g2o ..."

mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build . -j

cd ../../Sophus

echo "Configuring and building Thirdparty/Sophus ..."

mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build . -j

cd ../../../

rem Uncompressing vocabulary is no longer necessary with latest DBOW2. Also, DBOW2 seems to have deprecated the older format, so that's deleted anyway.
rem echo "Uncompress vocabulary ..."

rem cd Vocabulary
rem "C:\Program Files\7-Zip\7z.exe" x "ORBvoc.txt.tar.gz" -so | "C:\Program Files\7-Zip\7z.exe" x -si -ttar
rem cd ..

echo "Configuring and building ORB_SLAM3 ..."

mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build . -j4

pause 