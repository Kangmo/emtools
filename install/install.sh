#!/bin/sh
virtualenv env

APPLICATION_VENV=`pwd`/env
SITE_PACKAGES=`$APPLICATION_VENV/bin/python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())"`


echo "Installing application and dependencies (using binaries)"
$APPLICATION_VENV/bin/pip install --use-wheel --no-index --find-links=/opt/infinidb/em/python-stack/packages/whl/ --find-links=./packages/whl/ -r ./requirements.txt
echo ""
echo "Application virtualenv directory"
echo "$APPLICATION_VENV"
echo ""
echo "Site packages for virtualenv"
echo "$SITE_PACKAGES"
echo ""
echo "Install finished!"
echo ""
