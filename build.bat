@echo off

WHERE cmake
IF %ERRORLEVEL% NEQ 0 (
    ECHO cmake wasn't found 
    EXIT /B -1
)

if "%~1"=="" goto blank
vcpkg = "%~1"
goto endif1
blank:
WHERE vcpkg
IF %ERRORLEVEL% NEQ 0 (
    ECHO vcpkg wasn't found. Please add location as argument or download vcpkg.
    EXIT /B -1
)
endif1:

echo installing 

vcpkg install pangolin pangolin:x64-windows boost boost:x64-windows openssl openssl:x64-windows opencv opencv:x64-windows dlib dlib:x64-windows

echo "Configuring and building Thirdparty libraries ..."

cd Thirdparty
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build . -j

cd ../

mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build . -j4

pause 