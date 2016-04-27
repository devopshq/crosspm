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

function error {
    echo "$@" 1>&2

    exit 1
}

function bool() {
    local VALUE="$1"

    if [ "$VALUE" = true ]; then

        return 0
    elif [ "$VALUE" = false ]; then

        return 1
    fi

    error "ERROR: Wrong value for bool() required true or false (case sensitive) while value=${VALUE}"
}

function parse_branch() {

    local BRANCH_NAME="$1"
    local PULL_REQUEST="$2"

    local BUILD_RELEASE=false
    local BUILD_DEVELOP=false
    local BUILD_CI_INFO=false
    local BUILD_MERGE=false

    if [ "$PULL_REQUEST" != false ]; then

        BUILD_CI_INFO=true
        BUILD_MERGE=true
    else

        case $BRANCH_NAME in

        "master" | "release"[-_\/\\]* )
            BUILD_RELEASE=true
            ;;

        "develop" )
            BUILD_DEVELOP=true
            ;;

        *)
            BUILD_CI_INFO=true
            ;;
        esac

    fi

    echo "${BUILD_RELEASE} ${BUILD_DEVELOP} ${BUILD_CI_INFO} ${BUILD_MERGE}"
}

function extract_version_from_file() {

    local FILENAME="$1"
    local VERSION=$(cat "$FILENAME" | sed -n "s/^__version__\s*=\s*[\'\"]\(.\+\)[\'\"]/\1/p")

    [[ "$VERSION" ]] || error "ERROR: unable to extract version from file: $FILENAME"

    echo "$VERSION"
}

function version_append_build_number() {

    local FILENAME="$1"
    local BUILD_NU="$2"

    sed -i "s/^__version__\s*=\s*[\'\"]\(.\+\)[\'\"]/__version__ = \'\1.${BUILD_NU}\'/" $FILENAME
}

function test_travis_build_status_link() {

    local BUILD_STATUS_LINK="https://travis-ci.org/devopshq/crosspm.svg?branch="
    local BRANCH_URLENCODE=$(python3 -c "import urllib.parse; print(urllib.parse.quote_plus('$TRAVIS_BRANCH'))")

    cat README.rst | grep -q "${BUILD_STATUS_LINK}${BRANCH_URLENCODE}\$"
}

function test_tag_not_exists() {

    local TAG_VALUE="$1"
    [ "$(git tag -l ${TAG_VALUE})" ] && error "ERROR: git tag '${TAG_VALUE}' already exists"
}
