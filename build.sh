#!/bin/sh
echo "Cleaning virtualenv build directory if exists"
rm -rf ./build-env

echo "Building virtualenv build directory"
virtualenv build-env
BUILD_ENV=`pwd`/build-env
echo "Installing wheel"
./build-env/bin/pip install --no-index --find-link=./build-lib/ wheel

echo "Creating build directories for src / whl packages"
mkdir -p ./build-env/packages/src
mkdir -p ./build-env/packages/whl

echo "Cleaning dist directory if exists"
rm -rf ./dist

echo "copy site.properties.package"
cp ./conf/site.properties.package ./conf/site.properties

echo "Building src dist"
./build-env/bin/python setup.py sdist

echo "Building bdist_wheel dist"
./build-env/bin/pip wheel --no-deps --no-index --find-links=dist --wheel-dir dist infinidb-em-tools

echo "Creating version file"
echo "1.0.0" > ./dist/version

echo ""
echo "Finished!"

