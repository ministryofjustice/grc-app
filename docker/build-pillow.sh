#!/usr/bin/env bash
set -euo pipefail

# Rebuild the released wheel's native stack, changing only Brotli. Stock Debian
# codecs are not equivalent to Pillow's wheel (notably AVIF, OpenJPEG and Raqm).
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cd "$work"

fetch() {
    local name=$1 checksum=$2 url=$3
    curl --fail --silent --show-error --location --retry 3 --output "$name" "$url"
    printf '%s  %s\n' "$checksum" "$name" | sha256sum --check --strict
}

# Gitiles tar exports are not byte-stable. Git verifies the pinned commit and
# its complete object tree instead; never follow a mutable branch or tag here.
fetch_commit() {
    local name=$1 commit=$2 url=$3
    git init --quiet "$name"
    GIT_TERMINAL_PROMPT=0 git -C "$name" fetch --quiet --depth=1 "$url" "$commit"
    git -C "$name" checkout --quiet --detach FETCH_HEAD
    [[ "$(git -C "$name" rev-parse HEAD)" == "$commit" ]]
    rm -rf "$name/.git"
}

fetch pillow.tar.gz 0458511ac96e7d44e574484efff9c6210f8211046b3e7ec1dca2381cea0f8430 \
    https://codeload.github.com/python-pillow/Pillow/tar.gz/293218ad059d994baf1777d882911bed6a49704a
fetch multibuild.tar.gz e50c410a625333404ba318f109b082ff04b1edb1e18e92109e38897c9561db09 \
    https://codeload.github.com/matthew-brett/multibuild/tar.gz/c893f305c6066b6d940e10d3333be8cb27fa3947
fetch dependencies.tar.gz bebb7e92376e98273c9c2de1cac027c73e0074174788f0e65abcf5a60b70fa57 \
    https://codeload.github.com/python-pillow/pillow-depends/tar.gz/93950a8f9ada1165a4ab8c719326d5017e3f6c72
fetch brotli-1.2.1.tar.gz 98d35d11a78dc453aebb7d10c3748f3f73ff78c8267c0dc697b8631f67bf7e8f \
    https://codeload.github.com/google/brotli/tar.gz/refs/tags/v1.2.1
fetch_commit aom 03087864cf4bea6abb0d28f95cf7843511413d8f https://aomedia.googlesource.com/aom
fetch_commit libyuv 644251f252a84bf8ce91ff0aca86a9b16b069ab8 https://chromium.googlesource.com/libyuv/libyuv
fetch dav1d.tar.gz c5b7428c3f5b28db0aee0c62f6ffb2b42f4b08e7be5ce49d7ad046aaf0dc151d \
    https://codeload.github.com/videolan/dav1d/tar.gz/b546257f770768b2c88258c533da38b91a06f737

mkdir -p pillow
tar -xzf pillow.tar.gz -C pillow --strip-components=1
cd pillow
mkdir -p wheels/multibuild build/pillow-depends-main cgr-native/{dav1d,libwebp}
tar -xzf ../multibuild.tar.gz -C wheels/multibuild --strip-components=1
tar -xzf ../dependencies.tar.gz -C build/pillow-depends-main --strip-components=1
cp ../brotli-1.2.1.tar.gz build/pillow-depends-main/
rm build/pillow-depends-main/brotli-1.2.0.tar.gz
mv ../aom ../libyuv cgr-native/
tar -xzf ../dav1d.tar.gz -C cgr-native/dav1d --strip-components=1
tar -xzf build/pillow-depends-main/libwebp-1.6.0.tar.gz -C cgr-native/libwebp --strip-components=1
# Complete shared WebP before LCMS so AVIF's temporary static WebP archive cannot
# shadow the shared dependency while LCMS links its TIFF utility.
patch --batch --fuzz=0 -p1 < /build/pillow-brotli.patch

export CIBW_PLATFORM=linux CIBW_ARCHS=x86_64 AUDITWHEEL_ARCH=x86_64 AUDITWHEEL_POLICY=manylinux_2_36
export MAX_CONCURRENCY=4 PIP_NO_CACHE_DIR=1 PIP_NO_INDEX=1 PIP_CONSTRAINT=/build/pillow-build-requirements.txt
export BUILD_PREFIX=/usr/local
export CPPFLAGS="-I/usr/local/include${CPPFLAGS:+ $CPPFLAGS}"
export LDFLAGS="-L/usr/local/lib${LDFLAGS:+ $LDFLAGS}"
export LIBRARY_PATH=/usr/local/lib${LIBRARY_PATH:+:$LIBRARY_PATH}
export LD_LIBRARY_PATH=/usr/local/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}
export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig:/usr/local/share/pkgconfig
export CMAKE_PREFIX_PATH=/usr/local
# Upstream multibuild scripts deliberately support optional unset variables.
set +u
if ! bash .github/workflows/wheels-dependencies.sh > "$work/native-build.log" 2>&1; then
    tail -n 80 "$work/native-build.log"
    exit 1
fi
set -u
printf 'Pinned native dependencies built successfully\n'
ldconfig

python -m pip wheel --no-deps --no-cache-dir --no-build-isolation --wheel-dir "$work/raw" \
    -C jpeg=enable -C zlib=enable -C tiff=enable -C freetype=enable \
    -C raqm=enable -C raqm=vendor -C fribidi=vendor -C lcms=enable \
    -C webp=enable -C jpeg2000=enable -C xcb=enable -C avif=enable \
    -C imagequant=disable .
python -m auditwheel repair --plat manylinux_2_36_x86_64 --wheel-dir /wheelhouse "$work"/raw/*.whl
cp .github/dependencies.json /wheelhouse/native-dependencies.json
cp /build/pillow-build-requirements.txt /wheelhouse/build-requirements.txt
sha256sum /wheelhouse/*.whl > /wheelhouse/SHA256SUMS
