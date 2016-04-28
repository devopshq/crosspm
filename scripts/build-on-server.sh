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


DEVOPS_CHECKOUT_DIR="$(dirname "$(dirname "$(readlink --canonicalize --no-newline "${BASH_SOURCE:-$0}")")")"
cd "$DEVOPS_CHECKOUT_DIR"


. "scripts/common.sh"


DEVOPS_BUILD_BRANCH="$TRAVIS_BRANCH"
DEVOPS_BUILD_PULL_REQUEST_NUMBER="$TRAVIS_PULL_REQUEST"
DEVOPS_BUILD_NUMBER="$TRAVIS_BUILD_NUMBER"
DEVOPS_BUILD_DIR="$(pwd)/build"
DEVOPS_BUILD_VERSION_FROM_FILE="$(extract_version_from_file crosspm/__init__.py)"
DEVOPS_BUILD_VERSION="${DEVOPS_BUILD_VERSION_FROM_FILE}"

DEVOPS_BUILD_RELEASE=false
DEVOPS_BUILD_DEVELOP=false
DEVOPS_BUILD_CI_INFO=false
DEVOPS_BUILD_MERGE=false

read -r DEVOPS_BUILD_RELEASE DEVOPS_BUILD_DEVELOP DEVOPS_BUILD_CI_INFO DEVOPS_BUILD_MERGE <<< $(parse_branch $DEVOPS_BUILD_BRANCH $DEVOPS_BUILD_PULL_REQUEST_NUMBER)


if bool "$DEVOPS_BUILD_MERGE" || ! bool "$DEVOPS_BUILD_CI_INFO"; then

    echo "INFO: check README.rst contain correct url to travis build status"

    cat README.rst | grep -q "$(get_url_travis_build_status $DEVOPS_BUILD_BRANCH)\$" || error "ERROR: file README.rst contains incorrect url to travis build status"
fi

if bool "$DEVOPS_BUILD_DEVELOP"; then

    version_append_build_number "crosspm/__init__.py" "dev${DEVOPS_BUILD_NUMBER}"

    DEVOPS_BUILD_VERSION="$(extract_version_from_file crosspm/__init__.py)"

    echo "INFO: __version__ changed from '$DEVOPS_BUILD_VERSION_FROM_FILE' to '$DEVOPS_BUILD_VERSION'"
fi

echo "INFO: building"

rm -rf "$DEVOPS_BUILD_DIR"
mkdir -p "$DEVOPS_BUILD_DIR"

python3 setup.py egg_info sdist --dist-dir "$DEVOPS_BUILD_DIR" bdist_wheel --dist-dir "$DEVOPS_BUILD_DIR"

echo "INFO: content of build dir"
ls -l "$DEVOPS_BUILD_DIR"

echo "INFO: testing"

python3 setup.py test


if ! bool "$DEVOPS_BUILD_CI_INFO"; then

    echo "INFO: check git tag is not exists"

    DEVOPS_BUILD_GIT_TAG="v${DEVOPS_BUILD_VERSION}"

    git_tag_exists $DEVOPS_BUILD_GIT_TAG && error "ERROR: git tag '${DEVOPS_BUILD_VERSION}' already exists"

    git tag "$DEVOPS_BUILD_GIT_TAG"
    echo "git push origin $DEVOPS_BUILD_GIT_TAG"
    
    echo "need pypi upload"
fi
