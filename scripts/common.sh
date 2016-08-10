#!/usr/bin/env bash

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

function get_url_travis_build_status() {

    local BRANCH_NAME="$1"
    local BRANCH_URL_ENCODE=$(python3 -c "import urllib.parse; print(urllib.parse.quote_plus('$BRANCH_NAME'))")
    
    echo "https://travis-ci.org/devopshq/crosspm.svg?branch=${BRANCH_URL_ENCODE}"
}

function git_tag_exists() {

    local TAG_VALUE="$1"

    [ "$(git tag -l ${TAG_VALUE})" ]
}

function git_set_tag() {

    local TAG_VALUE="$1"
    local BUILD_ID="$2"

    git tag -a "$TAG_VALUE" -m"build log https://travis-ci.org/devopshq/crosspm/builds/${BUILD_ID}"
}

function set_flag_need_push_tags() {

    touch "./DEVOPS_FLAG_NEED_PUSH_TAGS"
}

function is_flag_need_push_tags() {

    [ -f "./DEVOPS_FLAG_NEED_PUSH_TAGS" ]
}