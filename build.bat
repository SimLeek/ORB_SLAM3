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

vcpkg install pangolin pangolin:x64-windows
vcpkg install boost boost:x64-windows
rem vcpkg install openblas[threads] openblas[threads]:x64-windows
vcpkg install openssl openssl:x64-windows
vcpkg install suitesparse suitesparse:x64-windows


rem .\vcpkg\vcpkg
WHERE nvcc
IF %ERRORLEVEL% NEQ 0 (
    ECHO CUDA wasn't found. Not installing cuda optimizations.
	ecgo please install cuda from: https://developer.nvidia.com/cuda-downloads for cuda support
	echo installing without cuda support
    
	vcpkg install opencv[core,default-features,dnn,jpeg,png,quirc,tiff,webp,eigen,ffmpeg,lapack,opengl,openmp,python,tbb] opencv[core,default-features,dnn,jpeg,png,quirc,tiff,webp,eigen,ffmpeg,lapack,opengl,openmp,python,tbb]:x64-windows
	vcpkg install dlib[fftw3] dlib[fftw3]:x64-windows
	
) else (
	echo installing 

	vcpkg install opencv[core,default-features,dnn,jpeg,png,quirc,tiff,webp,eigen,ffmpeg,lapack,opengl,openmp,python,tbb] opencv[core,default-features,dnn,jpeg,png,quirc,tiff,webp,cuda,cudnn,eigen,ffmpeg,lapack,opengl,openmp,python,tbb]:x64-windows
	vcpkg install dlib[fftw3] dlib[cuda,fftw3]:x64-windows
)

echo "Configuring and building Thirdparty libraries ..."

if %errorlevel% neq 0 exit /b %errorlevel%

cd Thirdparty
mkdir build
cmake --no-warn-unused-cli -DINSTALL_STEP:STRING=1 -DCMAKE_TOOLCHAIN_FILE:STRING=%vcpkg:~0,-6%/scripts/buildsystems/vcpkg.cmake -DCMAKE_EXPORT_COMPILE_COMMANDS:BOOL=TRUE -S. -B./build -G "Visual Studio 16 2019" -T host=x64 -A x64
cmake --build ./build --config Release --target ALL_BUILD -j 18 --
cmake --no-warn-unused-cli -DINSTALL_STEP:STRING=2 -DCMAKE_TOOLCHAIN_FILE:STRING=%vcpkg:~0,-6%/scripts/buildsystems/vcpkg.cmake -DCMAKE_EXPORT_COMPILE_COMMANDS:BOOL=TRUE -S. -B./build -G "Visual Studio 16 2019" -T host=x64 -A x64
cmake --build ./build --config Release --target ALL_BUILD -j 18 --

cd ../

mkdir build
cmake --no-warn-unused-cli -DCOMPILEDWITHC11:STRING=1 -DCMAKE_TOOLCHAIN_FILE:STRING=%vcpkg:~0,-6%/scripts/buildsystems/vcpkg.cmake -DCMAKE_EXPORT_COMPILE_COMMANDS:BOOL=TRUE -S. -B./build -G "Visual Studio 16 2019" -T host=x64 -A x64
cmake --build ./build --config Release --target ALL_BUILD -j 18 --

pause 