#!/bin/bash

set -e

APP_NAME="mypl"
VERSION="1.0"
ARCH="all"
OUT_DIR="pkg"

# Clean previous build
rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR/DEBIAN"
mkdir -p "$OUT_DIR/usr/bin"
mkdir -p "$OUT_DIR/usr/lib/python3/dist-packages/"

echo "Setting up control file..."

# Create control file
cat <<EOF > "$OUT_DIR/DEBIAN/control"
Package: $APP_NAME
Version: $VERSION
Section: utils
Priority: optional
Architecture: $ARCH
Maintainer: Caleb Lefcort <clefcort@zagmail.gonzaga.edu>
Depends: python3
Description: MyPL - A simple interpreted programming language
EOF

echo "Copying program files..."

# Copy the runner script
cp bin/mypl "$OUT_DIR/usr/bin/mypl"
chmod +x "$OUT_DIR/usr/bin/mypl"

# Copy the mpl/ library
cp -r bin/mpl/ "$OUT_DIR/usr/lib/python3/dist-packages/"

echo "Building .deb package..."

# Build the deb package
dpkg-deb --build "$OUT_DIR" "${APP_NAME}_${VERSION}.deb"

echo "Done! Built ${APP_NAME}_${VERSION}.deb"
