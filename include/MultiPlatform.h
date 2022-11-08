#ifndef MULTIPLATFORM_H
#define MULTIPLATFORM_H

#ifdef _WIN32
    #if COMPILING_DLL
        #define DLLEXPORT __declspec(dllexport)
    #else
        #define DLLEXPORT __declspec(dllimport)
    #endif
#else
    #define DLLEXPORT
#endif

#endif
