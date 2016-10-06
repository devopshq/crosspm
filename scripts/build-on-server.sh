#!/usr/bin/env bash

set -e -v -x


DEVOPS_CHECKOUT_DIR="$(dirname "$(dirname "$(readlink --canonicalize --no-newline "${BASH_SOURCE:-$0}")")")"
cd "$DEVOPS_CHECKOUT_DIR"

. "./scripts/common.sh"


# TODO: check we are under travis - why?
# TODO: check version has correct syntax
# TODO: check release branch version correlate to __version__


DEVOPS_BUILD_BRANCH="$TRAVIS_BRANCH"
DEVOPS_BUILD_PULL_REQUEST_NUMBER="$TRAVIS_PULL_REQUEST"
DEVOPS_BUILD_NUMBER="$TRAVIS_BUILD_NUMBER"
DEVOPS_BUILD_ID="$TRAVIS_BUILD_ID"
DEVOPS_BUILD_DIR="$(pwd)/build"
DEVOPS_BUILD_VERSION_FROM_FILE="$(extract_version_from_file crosspm/__init__.py)"
DEVOPS_BUILD_VERSION="${DEVOPS_BUILD_VERSION_FROM_FILE}"

echo "$TRAVIS_BUILD_NUMBER"

DEVOPS_BUILD_RELEASE=false
DEVOPS_BUILD_DEVELOP=false
DEVOPS_BUILD_CI_INFO=false
DEVOPS_BUILD_MERGE=false

read -r DEVOPS_BUILD_RELEASE DEVOPS_BUILD_DEVELOP DEVOPS_BUILD_CI_INFO DEVOPS_BUILD_MERGE <<< $(parse_branch $DEVOPS_BUILD_BRANCH $DEVOPS_BUILD_PULL_REQUEST_NUMBER)


if bool "$DEVOPS_BUILD_MERGE" || ! bool "$DEVOPS_BUILD_CI_INFO"; then

    echo "INFO:  ======== check README.rst contain correct url to travis build status"

    cat README.rst | grep -q "$(get_url_travis_build_status $DEVOPS_BUILD_BRANCH)\$" || error "ERROR: file README.rst contains incorrect url to travis build status"
fi

if bool "$DEVOPS_BUILD_DEVELOP"; then

    version_append_build_number "crosspm/__init__.py" "dev${DEVOPS_BUILD_NUMBER}"

    DEVOPS_BUILD_VERSION="$(extract_version_from_file crosspm/__init__.py)"

    echo "INFO:  ======== __version__ changed from '$DEVOPS_BUILD_VERSION_FROM_FILE' to '$DEVOPS_BUILD_VERSION'"
fi

echo "INFO: ======== building..."

rm -rf "$DEVOPS_BUILD_DIR"
mkdir -p "$DEVOPS_BUILD_DIR"

python3 setup.py egg_info sdist --dist-dir "$DEVOPS_BUILD_DIR" bdist_wheel --dist-dir "$DEVOPS_BUILD_DIR"

echo "INFO:  ======== content of build dir"
ls -l "$DEVOPS_BUILD_DIR"

echo "INFO:  ======== testing..."

python3 setup.py test


if ! bool "$DEVOPS_BUILD_CI_INFO"; then

    echo "INFO: ========  check git tag is not exists"

    DEVOPS_BUILD_GIT_TAG="v${DEVOPS_BUILD_VERSION}"

    git_tag_exists "$DEVOPS_BUILD_GIT_TAG" && error "ERROR: git tag '${DEVOPS_BUILD_VERSION}' already exists"

    git_set_tag "$DEVOPS_BUILD_GIT_TAG" "$DEVOPS_BUILD_ID"

    git_tag_exists "$DEVOPS_BUILD_GIT_TAG" || error "ERROR: git tag was not set"

    set_flag_need_push_tags
    
    echo "INFO: ======== need pypi upload"
fi
