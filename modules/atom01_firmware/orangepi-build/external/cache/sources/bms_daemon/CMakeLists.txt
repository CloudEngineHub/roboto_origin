cmake_minimum_required(VERSION 3.12)

# 版本号与 debian/changelog 保持一致
project(roboto_bms VERSION 1.2.0)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3")
if(NOT CMAKE_CROSSCOMPILING)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -march=native")
endif()
set(CMAKE_CXX_COMPILER_LAUNCHER ccache)

set(THREADS_PREFER_PTHREAD_FLAG ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(CMAKE_BUILD_TYPE Release)

find_package(spdlog REQUIRED)
find_package(fmt REQUIRED)
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 REQUIRED)

set(PUBLIC_DEPENDENCIES
    fmt::fmt spdlog::spdlog pthread)

add_subdirectory(src/drivers)

# ---- Daemon executable ----
add_executable(bms_daemon
    src/bms_daemon.cpp
)
target_include_directories(bms_daemon PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_link_libraries(bms_daemon PRIVATE tws_bms_protocol fmt::fmt spdlog::spdlog pthread)

# ---- Client library ----
add_library(bms STATIC
    src/bms_driver.cpp
)
target_include_directories(bms
    PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)
target_link_libraries(bms PUBLIC ${PUBLIC_DEPENDENCIES} tws_bms)

# ---- Python bindings ----
pybind11_add_module(bms_py src/pybind_module.cpp)
target_link_libraries(bms_py PUBLIC bms)

# ---- Install ----
install(DIRECTORY include/ DESTINATION include)

install(TARGETS bms_daemon DESTINATION bin)

install(TARGETS bms tws_bms
    EXPORT roboto_bms-targets
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
    INCLUDES DESTINATION include
)

install(EXPORT roboto_bms-targets
  FILE roboto_bmsTargets.cmake
  NAMESPACE roboto_bms::
  DESTINATION lib/cmake/roboto_bms
)

include(CMakePackageConfigHelpers)

write_basic_package_version_file(
  "${CMAKE_CURRENT_BINARY_DIR}/roboto_bmsConfigVersion.cmake"
  VERSION ${PROJECT_VERSION}
  COMPATIBILITY AnyNewerVersion
)

configure_package_config_file(
  "${CMAKE_CURRENT_SOURCE_DIR}/cmake/roboto_bmsConfig.cmake.in"
  "${CMAKE_CURRENT_BINARY_DIR}/roboto_bmsConfig.cmake"
  INSTALL_DESTINATION lib/cmake/roboto_bms
)

# Install auto-generated Config for non-ROS consumers (Deb mode)
install(FILES 
  "${CMAKE_CURRENT_BINARY_DIR}/roboto_bmsConfig.cmake"
  "${CMAKE_CURRENT_BINARY_DIR}/roboto_bmsConfigVersion.cmake"
  DESTINATION lib/cmake/roboto_bms
)

set(PYTHON_INSTALL_DIR "lib/python${Python3_VERSION_MAJOR}.${Python3_VERSION_MINOR}/site-packages")
install(TARGETS bms_py
    LIBRARY DESTINATION ${PYTHON_INSTALL_DIR}
    ARCHIVE DESTINATION ${PYTHON_INSTALL_DIR}
    RUNTIME DESTINATION ${PYTHON_INSTALL_DIR}
)

