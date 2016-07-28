#!/bin/bash

set -e
set -x

#MIN CODE FOR LOCAL BUILD:
#
# export OutDirectory="/home/user/src/teamcity_output"
# export DEVOPS_ARTIFACTS_TASKS_FILE="/home/user/src/teamcity_output_package/artifacts_tasks.txt"
# export DEVOPS_OUT_PACKAGE_DIR="/home/user/src/teamcity_output_package"
# export DEVOPS_BUILD_NUMBER="1"
# export DEVOPS_BUILD_SUFFIX="feature-python-package"
# rm -rf "$OutDirectory"
# mkdir -p "$OutDirectory"
# rm -rf "$DEVOPS_OUT_PACKAGE_DIR"
# mkdir -p "$DEVOPS_OUT_PACKAGE_DIR"

#MIN CODE FOR LOCAL BUILD:

cd "$1"

CURRENT_DIR="$1"
BUILD_DIR="$CURRENT_DIR/build"
PYPI_REPO_NAME="devopshq-pypi"
PACKAGE_NAME="crosspm"
VERSION_TAG=".${DEVOPS_BUILD_NUMBER}${DEVOPS_BUILD_SUFFIX}"
VERSION_TAG=${VERSION_TAG//-/_}

rm -rf build
mkdir -p "$BUILD_DIR"

. /home/user/venv/bin/activate

python setup.py egg_info --tag-build="$VERSION_TAG" sdist --dist-dir "$BUILD_DIR" bdist_wheel --dist-dir "$BUILD_DIR"

SDIST_PACKAGE_FILENAME=$(ls -1 ${BUILD_DIR}/${PACKAGE_NAME}-*.tar.gz)
SDIST_PACKAGE_VERSION=$(sed -n "s/.\+\/${PACKAGE_NAME}-\(.\+\).tar.gz/\1/p" <<< $SDIST_PACKAGE_FILENAME)

BDIST_PACKAGE_FILENAME=$(ls -1 ${BUILD_DIR}/${PACKAGE_NAME}-*.whl)
BDIST_PACKAGE_VERSION=$(sed -n "s/.\+\/${PACKAGE_NAME}-\(.\+\).whl/\1/p" <<< $BDIST_PACKAGE_FILENAME)

#cp -v $SDIST_PACKAGE_FILENAME $OutDirectory
#cp -v $BDIST_PACKAGE_FILENAME $OutDirectory

cp -v $SDIST_PACKAGE_FILENAME $DEVOPS_OUT_PACKAGE_DIR
cp -v $BDIST_PACKAGE_FILENAME $DEVOPS_OUT_PACKAGE_DIR

SDIST_PACKAGE_NAME=$(basename $SDIST_PACKAGE_FILENAME)
BDIST_PACKAGE_NAME=$(basename $BDIST_PACKAGE_FILENAME)

echo "${SDIST_PACKAGE_NAME};${PYPI_REPO_NAME}/${PACKAGE_NAME}/$SDIST_PACKAGE_VERSION/${SDIST_PACKAGE_NAME}" >> "$DEVOPS_ARTIFACTS_TASKS_FILE"
# use $SDIST_PACKAGE_VERSION as version here
echo "${BDIST_PACKAGE_NAME};${PYPI_REPO_NAME}/${PACKAGE_NAME}/$SDIST_PACKAGE_VERSION/${BDIST_PACKAGE_NAME}" >> "$DEVOPS_ARTIFACTS_TASKS_FILE"

echo "upload list:"
cat "$DEVOPS_ARTIFACTS_TASKS_FILE"
