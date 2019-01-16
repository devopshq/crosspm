#!/usr/bin/env bash
find ./docs/ -name "*.md" | xargs bash gh-md-toc --insert