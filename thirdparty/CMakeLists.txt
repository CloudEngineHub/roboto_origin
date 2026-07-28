# SPDX-License-Identifier: GPL-3.0-only

include(FetchContent)

if(CMAKE_SYSTEM_PROCESSOR STREQUAL "x86_64")
    set(ONNXRUNTIME_NAME "onnxruntime-linux-x64-1.21.0")
    set(ONNXRUNTIME_HASH "SHA256=7485c7e7aac6501b27e353dcbe068e45c61ab51fbaf598d13970dfae669d20bf")
elseif(CMAKE_SYSTEM_PROCESSOR STREQUAL "aarch64")
    set(ONNXRUNTIME_NAME "onnxruntime-linux-aarch64-1.21.0")
    set(ONNXRUNTIME_HASH "SHA256=4508084bde1232ee1ab4b6fad2155be0ea2ccab1c1aae9910ddb3fb68a60805e")
else()
    message(FATAL_ERROR "Unsupported architecture: ${CMAKE_SYSTEM_PROCESSOR}")
endif()

message(STATUS "Architecture detected: ${CMAKE_SYSTEM_PROCESSOR}. Using ${ONNXRUNTIME_NAME}")

set(ONNXRUNTIME_LOCAL "${CMAKE_CURRENT_LIST_DIR}/${ONNXRUNTIME_NAME}.tgz")
set(ONNXRUNTIME_URL "https://github.com/microsoft/onnxruntime/releases/download/v1.21.0/${ONNXRUNTIME_NAME}.tgz")

if(EXISTS "${ONNXRUNTIME_LOCAL}")
    message(STATUS "ONNX Runtime: using local tarball ${ONNXRUNTIME_LOCAL}")
    set(ONNXRUNTIME_URL "${ONNXRUNTIME_LOCAL}")
endif()

FetchContent_Declare(
    onnxruntime_camera
    URL      "${ONNXRUNTIME_URL}"
    URL_HASH ${ONNXRUNTIME_HASH}
    SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}/onnxruntime"
)

FetchContent_MakeAvailable(onnxruntime_camera)

set(ONNXRUNTIME_INCLUDE_DIR "${CMAKE_CURRENT_LIST_DIR}/onnxruntime/include")
set(ONNXRUNTIME_LIB_DIR "${CMAKE_CURRENT_LIST_DIR}/onnxruntime/lib")
set(ONNXRUNTIME_LIB_FILE "${ONNXRUNTIME_LIB_DIR}/libonnxruntime.so")

set(ONNXRUNTIME_INCLUDE_DIR ${ONNXRUNTIME_INCLUDE_DIR} PARENT_SCOPE)
set(ONNXRUNTIME_LIB_DIR ${ONNXRUNTIME_LIB_DIR} PARENT_SCOPE)
set(ONNXRUNTIME_LIB_FILE ${ONNXRUNTIME_LIB_FILE} PARENT_SCOPE)
