cmake_minimum_required(VERSION 2.8.11)

include(ExternalProject)

set(Python_ADDITIONAL_VERSIONS 3.0 3.1 3.2 3.3 3.4 3.5)

find_package(PythonInterp)


set(CPM_DIR ${CMAKE_CURRENT_LIST_DIR})


function(pm_download_dependencies)

    _pm_download_dependencies( ${CMAKE_SOURCE_DIR} ${CMAKE_BINARY_DIR} )

endfunction()


function(pm_download_current_dependencies)

    _pm_download_dependencies( ${CMAKE_CURRENT_SOURCE_DIR} ${CMAKE_CURRENT_BINARY_DIR} )

endfunction()


function(_pm_download_dependencies SOURCE_DIR BINARY_DIR)

    if(NOT DEFINED CPM_TARGET_OS)
        if("x$ENV{TargetOS}" STREQUAL "x")
            message(FATAL_ERROR "Env var TargetOS not set!")
        else()
            set(CPM_TARGET_OS $ENV{TargetOS} CACHE STRING "CMAKE Package Manager variable" FORCE)
        endif()
    endif()

    if(NOT DEFINED CPM_TARGET_ARCH)
        if("x$ENV{TargetArchitecture}" STREQUAL "x")
            message(FATAL_ERROR "Env var TargetArchitecture not set!")
        else()
            set(CPM_TARGET_ARCH $ENV{TargetArchitecture} CACHE STRING "CMAKE Package Manager variable" FORCE)
        endif()
    endif()

    if(NOT DEFINED CPM_PLATFORM_TOOLSET)
        if("x$ENV{PlatformToolset}" STREQUAL "x")
            message(FATAL_ERROR "Env var PlatformToolset not set!")
        else()
            set(CPM_PLATFORM_TOOLSET $ENV{PlatformToolset} CACHE STRING "CMAKE Package Manager variable" FORCE)
        endif()
    endif()

    execute_process(
        COMMAND
            "${PYTHON_EXECUTABLE}"
            "-u"
            "-m" "crosspm"
            "download"
            "-o"
            "os=${CPM_TARGET_OS},arch=${CPM_TARGET_ARCH},cl=${CPM_PLATFORM_TOOLSET}"
        WORKING_DIRECTORY
            "${SOURCE_DIR}"
        OUTPUT_FILE
            "${BINARY_DIR}/tmp_packages.deps"
        RESULT_VARIABLE
            RESULT_CODE_VALUE
    )

    if(NOT "${RESULT_CODE_VALUE}" STREQUAL "0")
        message(FATAL_ERROR "process failed RESULT_CODE='${RESULT_CODE_VALUE}'")
    endif()

    # read file to variable
    file(STRINGS "${BINARY_DIR}/tmp_packages.deps" FILE_CONTENT)

    # count lines
    list(LENGTH FILE_CONTENT FILE_CONTENT_LENGTH)

    # calc: max_i = n - 1
    math(EXPR FILE_CONTENT_N "${FILE_CONTENT_LENGTH} - 1")


    # iterate over lines
    foreach(FILE_CONTENT_I RANGE ${FILE_CONTENT_N})
        list(GET FILE_CONTENT ${FILE_CONTENT_I} LINE_VALUE)

        string(STRIP "${LINE_VALUE}" LINE_VALUE)

        if(NOT "${LINE_VALUE}" STREQUAL "")
            # split line to list
            string(REPLACE ": " ";" LINE_VARS_LIST ${LINE_VALUE})

            # get vars from list
            list(GET LINE_VARS_LIST 0 VAR_PACKAGE_NAME)
            list(GET LINE_VARS_LIST 1 VAR_PACKAGE_PATH)

            string(STRIP "${VAR_PACKAGE_NAME}" VAR_PACKAGE_NAME)
            string(STRIP "${VAR_PACKAGE_PATH}" VAR_PACKAGE_PATH)

            # add cmake package
            _pm_add_package(${VAR_PACKAGE_NAME} ${VAR_PACKAGE_PATH})
        endif()
    endforeach()




endfunction()


function(_pm_add_package PACKAGE_NAME PACKAGE_PATH)

    message(STATUS "Load package '${PACKAGE_NAME}' from '${PACKAGE_PATH}'")

    if(CPM_PACKAGE_${PACKAGE_NAME} AND NOT CPM_PACKAGE_${PACKAGE_NAME} STREQUAL ${PACKAGE_PATH})
        message(FATAL_ERROR "CPM package '${PACKAGE_NAME}' already loaded from ${CPM_PACKAGE_${PACKAGE_NAME}}")
    else()
        set(CPM_PACKAGE_${PACKAGE_NAME} ${PACKAGE_PATH} CACHE STRING "CMAKE Package Manager guard" FORCE)
    endif()

    if (EXISTS "${PACKAGE_PATH}/_pm_package.cmake")
        include( "${PACKAGE_PATH}/_pm_package.cmake" NO_POLICY_SCOPE  )
        pm_add_lib( ${PACKAGE_PATH} )
    else()
        message(STATUS "There is no _pm_package.cmake try to autogenerate target")
        _pm_add_package_auto(${PACKAGE_NAME} ${PACKAGE_PATH})
    endif()
endfunction()

function(_pm_add_package_auto PACKAGE_NAME PACKAGE_PATH)

    string(TOUPPER ${PACKAGE_NAME} TARGET_IMPORTED_NAME)

    if(NOT TARGET ${TARGET_IMPORTED_NAME})
        add_library(${TARGET_IMPORTED_NAME} INTERFACE)
        target_include_directories(${TARGET_IMPORTED_NAME} INTERFACE
            $<BUILD_INTERFACE:${PACKAGE_PATH}/include>
        )
    endif()

endfunction()
