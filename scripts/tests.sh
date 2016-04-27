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

. assert.sh --verbose

. common.sh

assert_raises "bool true" 0
assert_raises "bool false" 1
assert_raises "bool true" 0
assert_raises "bool QWERTY 2>&1" 1
assert "bool QWERTY 2>&1 | grep -q 'ERROR.*value=QWERTY'"

# positive tests
assert "parse_branch master false" "true false false false"
assert "parse_branch master 15" "false false true true"
assert "parse_branch develop false" "false true false false"
assert "parse_branch release-1.0 false" "true false false false"
assert "parse_branch release_1.0 false" "true false false false"
assert "parse_branch release/1.0 false" "true false false false"
assert "parse_branch release\\\\1.0 false" "true false false false"
assert "parse_branch feature/issue_18 false" "false false true false"

# negative tests
assert "parse_branch release false" "false false true false"
assert "parse_branch release1.0/ false" "false false true false"

# prepere next tests
AA=$(tempfile)
BB=$(tempfile)
printf "\nSOME TEXT\n__version__ = '1.2.3'\n" > $AA;
printf "\nSOME TEXT\n__version__ = 1.2.3\n" > $BB;

assert "extract_version_from_file $AA" "1.2.3"
assert_raises "extract_version_from_file $BB" 1
assert "extract_version_from_file $BB 2>&1 | grep -q 'ERROR.*version.*$BB'"

assert "version_append_build_number $AA dev33"
assert "extract_version_from_file $AA" "1.2.3.dev33"

# end of test suite
assert_end "build-on-server.sh"