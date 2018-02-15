Usage
=======
You can use Crosspm in cmake. It will help to download the libraries recursively and connect them to the project.
The root of the project must contain the dependencies.txt.lock  with libraries to download from the repository.
An example of dependencies.txt.lock:

```python
zlib                 1.2.8.199            1.2.8-pm
```
Place a file crosspm.cmake to your project. The file is available after downloading crosspm.
crosspm.cmake downloads the libraries specified in dependencies.txt.lock and then looks there for the _pm_package file,
which contains the import logic of a specific library into the calling project.
An example of _pm_package.cmake:

```shell

function(pm_add_lib ZLIB_ROOT)
    message("ZLIB_ROOT = ${ZLIB_ROOT}")

    if(NOT TARGET ZLIB)
        set(TARGET_IMPORTED_NAME ZLIB)
        add_library(${TARGET_IMPORTED_NAME} STATIC IMPORTED GLOBAL)
        set_property(TARGET ${TARGET_IMPORTED_NAME} PROPERTY INTERFACE_INCLUDE_DIRECTORIES "${ZLIB_ROOT}/include")

        if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_COMPILER_IS_CLANGXX)
            if(UNIX)
                set_property(TARGET ${TARGET_IMPORTED_NAME} PROPERTY IMPORTED_LOCATION "${ZLIB_ROOT}/lib/libz.a")
            elseif(WIN32)
                set_property(TARGET ${TARGET_IMPORTED_NAME} PROPERTY IMPORTED_LOCATION "${ZLIB_ROOT}/lib/libzlibstatic.a")
            endif()
        elseif(MSVC)
            set_property(TARGET ${TARGET_IMPORTED_NAME} PROPERTY IMPORTED_LOCATION_DEBUG       "${ZLIB_ROOT}/lib/zlibstaticd.lib")
            set_property(TARGET ${TARGET_IMPORTED_NAME} PROPERTY IMPORTED_LOCATION_RELEASE     "${ZLIB_ROOT}/lib/zlibstatic.lib")
        endif()
    endif()
endfunction()

```

You just have to add in CMakeLists.txt:

```python
include(crosspm)
pm_download_dependencies()
...
target_link_libraries(
ZLIB
)
```

