#!/usr/bin/env bash
set -e
FILES=$(find ./docs/ -name "*.md")
BASE=$(pwd)
for f in ${FILES}:
do
    dir=$(dirname ${f})
    filename=$(basename ${f})
    pushd ${dir}
    ${BASE}/gh-md-toc --insert ${filename}
    popd
done
