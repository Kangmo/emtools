#!/bin/sh
VERSION=`cat VERSION`
echo "Packaging tools $VERSION"

TOOLS_TARGET_DIR="tools-$VERSION"

echo "Cleaning target"
rm -rf target
mkdir -p target/$TOOLS_TARGET_DIR
echo "Packaging install"
cp ./install/* target/$TOOLS_TARGET_DIR/.
mkdir -p target/$TOOLS_TARGET_DIR/packages/src
mkdir -p target/$TOOLS_TARGET_DIR/packages/whl
cp ./dist/*.tar.gz target/$TOOLS_TARGET_DIR/packages/src
cp ./dist/*.whl target/$TOOLS_TARGET_DIR/packages/whl
cp ./dist/version target/$TOOLS_TARGET_DIR/packages
cd target
echo "Creating distribution artifact"
tar czf infinidb-em-tools-$VERSION.tar.gz $TOOLS_TARGET_DIR
echo "Finished!"
