cmake_minimum_required(VERSION 3.13)
project(DoorControl C CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(GEN_DIR ${CMAKE_CURRENT_SOURCE_DIR}/gen)
set(SRC_DIR ${CMAKE_CURRENT_SOURCE_DIR}/src)

# Resolve workspace root (go up from examples/DoorControl -> examples -> workspace)
set(WORKSPACE_ROOT "${CMAKE_CURRENT_SOURCE_DIR}")
get_filename_component(WORKSPACE_ROOT "${WORKSPACE_ROOT}" DIRECTORY)
get_filename_component(WORKSPACE_ROOT "${WORKSPACE_ROOT}" DIRECTORY)

set(BUILD_DIR "${WORKSPACE_ROOT}/build")
set(INSTALL_PREFIX "${BUILD_DIR}/install")

set(COMMONAPI_INCLUDE ${INSTALL_PREFIX}/install/usr/local/include/CommonAPI-3.2)
set(COMMONAPI_SOMEIP_INCLUDE ${WORKSPACE_ROOT}/libs/capicxx-someip-runtime/include)
set(VSOMEIP_INCLUDE ${WORKSPACE_ROOT}/libs/vsomeip/interface)
set(COMMONAPI_LIB ${INSTALL_PREFIX}/install/usr/local/lib)
set(COMMONAPI_SOMEIP_LIB ${INSTALL_PREFIX}/lib)
set(VSOMEIP_LIB ${BUILD_DIR}/vsomeip)

include_directories(
    ${GEN_DIR}
    ${SRC_DIR}
    ${COMMONAPI_INCLUDE}
    ${COMMONAPI_SOMEIP_INCLUDE}
    ${VSOMEIP_INCLUDE}
)

link_directories(
    ${COMMONAPI_LIB}
    ${COMMONAPI_SOMEIP_LIB}
    ${VSOMEIP_LIB}
)

# Service executable
add_executable(door_control_service
    ${SRC_DIR}/DoorControlService.cpp
    ${SRC_DIR}/DoorControlStubImpl.cpp
    ${GEN_DIR}/v1/vehicle/doors/DoorControlSomeIPDeployment.cpp
    ${GEN_DIR}/v1/vehicle/doors/DoorControlSomeIPStubAdapter.cpp
    ${GEN_DIR}/v1/vehicle/doors/DoorControlSomeIPProxy.cpp
)

target_link_libraries(door_control_service
    CommonAPI
    CommonAPI-SomeIP
    vsomeip3
    pthread
)

# Client executable
add_executable(door_control_client
    ${SRC_DIR}/DoorControlClient.cpp
    ${GEN_DIR}/v1/vehicle/doors/DoorControlSomeIPDeployment.cpp
    ${GEN_DIR}/v1/vehicle/doors/DoorControlSomeIPStubAdapter.cpp
    ${GEN_DIR}/v1/vehicle/doors/DoorControlSomeIPProxy.cpp
)

target_link_libraries(door_control_client
    CommonAPI
    CommonAPI-SomeIP
    vsomeip3
    pthread
)
