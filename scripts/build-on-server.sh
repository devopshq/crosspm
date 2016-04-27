#!/usr/bin/env bash

# The MIT License (MIT)
# 
# Copyright (c) 2015 Iaroslav Akimov <iaroslavscript@gmail.com>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


set -e
#set -x


. "scripts/common.sh"

export DEVOPS_BUILD_BRANCH="$TRAVIS_BRANCH"
export DEVOPS_BUILD_PULL_REQUEST_NUMBER="$TRAVIS_PULL_REQUEST"
export DEVOPS_BUILD_NUMBER="$TRAVIS_BUILD_NUMBER"

export DEVOPS_BUILD_RELEASE=false
export DEVOPS_BUILD_DEVELOP=false
export DEVOPS_BUILD_CI_INFO=false
export DEVOPS_BUILD_MERGE=false

read -r DEVOPS_BUILD_RELEASE DEVOPS_BUILD_DEVELOP DEVOPS_BUILD_CI_INFO DEVOPS_BUILD_MERGE <<< $(parse_branch $DEVOPS_BUILD_BRANCH $DEVOPS_BUILD_PULL_REQUEST_NUMBER)


if {bool "$DEVOPS_BUILD_MERGE"} || {! bool "$DEVOPS_BUILD_CI_INFO"}; then

    echo "need check build status link at README"
fi

if bool "$DEVOPS_BUILD_DEVELOP"; then

    echo "need update __version__"

    version_append_build_number "crosspm/__init__.py" "${DEVOPS_BUILD_NUMBER}"
fi

if ! bool "$DEVOPS_BUILD_CI_INFO"; then

    echo "need check tag is not exists"
    echo "need pypi upload"
    echo "need git tag"
fi

# ----------- build -------------------
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

python3 setup.py egg_info sdist --dist-dir "$BUILD_DIR" bdist_wheel --dist-dir "$BUILD_DIR"

# ----------- tests -------------------
python3 setup.py test

error "ERROR: not implemented"


#r'release[/\](?P<major>\d+)\.(?P<minor>\d+)(?P<patch>\.\d+)?'





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

rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

#. /home/user/venv/bin/activate


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
