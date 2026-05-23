#!/bin/bash
# 02-build-libs.sh - Build all runtime libraries
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUILD="$ROOT/build"
LIBS="$ROOT/libs"

reset_stale_cmake_cache() {
  local build_dir="$1"
  local source_dir="$2"
  local cache="$build_dir/CMakeCache.txt"

  if [ -f "$cache" ] && ! grep -Fqx "CMAKE_HOME_DIRECTORY:INTERNAL=$source_dir" "$cache"; then
    echo "=== Removing stale CMake cache: $build_dir ==="
    rm -rf "$build_dir"
  fi
}

stub_optional_vsomeip_dir() {
  local source_dir="$LIBS/vsomeip/$1"

  if [ ! -f "$source_dir/CMakeLists.txt" ]; then
    echo "=== Stubbing trimmed optional vsomeip directory: $1 ==="
    mkdir -p "$source_dir"
    : > "$source_dir/CMakeLists.txt"
  fi
}

prepare_trimmed_vsomeip_source() {
  stub_optional_vsomeip_dir "examples"
  stub_optional_vsomeip_dir "examples/routingmanagerd"
  stub_optional_vsomeip_dir "examples/hello_world"
  stub_optional_vsomeip_dir "examples/wait-until-available"
  stub_optional_vsomeip_dir "tools/vsomeip_ctrl"
  stub_optional_vsomeip_dir "test"
}

prepare_trimmed_commonapi_source() {
  if [ ! -f "$LIBS/capicxx-core-runtime/commonapi.spec.in" ]; then
    echo "=== Stubbing trimmed CommonAPI RPM spec template ==="
    : > "$LIBS/capicxx-core-runtime/commonapi.spec.in"
  fi
}

echo "=== Building vsomeip ==="
prepare_trimmed_vsomeip_source
reset_stale_cmake_cache "$BUILD/vsomeip" "$LIBS/vsomeip"
cmake -S "$LIBS/vsomeip" -B "$BUILD/vsomeip" -DCMAKE_BUILD_TYPE=RelWithDebInfo
cmake --build "$BUILD/vsomeip" --parallel "$(nproc)"

echo "=== Building CommonAPI Core runtime ==="
prepare_trimmed_commonapi_source
reset_stale_cmake_cache "$BUILD/capicxx-core-runtime" "$LIBS/capicxx-core-runtime"
cmake -S "$LIBS/capicxx-core-runtime" -B "$BUILD/capicxx-core-runtime" \
  -DCMAKE_INSTALL_PREFIX=/usr/local
cmake --build "$BUILD/capicxx-core-runtime" --parallel "$(nproc)"
DESTDIR="$BUILD/install/install" cmake --install "$BUILD/capicxx-core-runtime"

echo "=== Building CommonAPI SOME/IP runtime ==="
reset_stale_cmake_cache "$BUILD/capicxx-someip-runtime" "$LIBS/capicxx-someip-runtime"
cmake -S "$LIBS/capicxx-someip-runtime" -B "$BUILD/capicxx-someip-runtime" \
  -DCMAKE_INSTALL_PREFIX="$BUILD/install" \
  -DUSE_INSTALLED_COMMONAPI=OFF \
  "-DCMAKE_PREFIX_PATH=$BUILD/install/install/usr/local;$BUILD/vsomeip"
cmake --build "$BUILD/capicxx-someip-runtime" --parallel "$(nproc)"
cmake --install "$BUILD/capicxx-someip-runtime"

echo "=== All libraries built ==="
ls "$BUILD/vsomeip"/*.so
ls "$BUILD/capicxx-core-runtime"/*.so
ls "$BUILD/capicxx-someip-runtime"/*.so
