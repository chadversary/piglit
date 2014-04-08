#
# Copyright (c) 2012 Intel Corporation
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# This permission notice shall be included in all copies or
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE AUTHOR(S) BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN
# AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF
# OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import os
import re
import sys
import subprocess

from os import path
from framework.core import TestProfile, TestResult
from framework.exectest import Test, TEST_BIN_DIR

__all__ = ['profile']

#############################################################################
##### IGTTest: Execute an intel-gpu-tools test
#####
##### To use this, create an igt symlink in piglit/bin which points to the root
##### of the intel-gpu-tools sources with the compiled tests. Piglit will
##### automatically add all tests into the 'igt' category.
#############################################################################

def checkEnvironment():
    debugfs_path = "/sys/kernel/debug/dri"
    if os.getuid() != 0:
        print "Test Environment check: not root!"
        return False
    if not os.path.isdir(debugfs_path):
        print "Test Environment check: debugfs not mounted properly!"
        return False
    for subdir in os.listdir(debugfs_path):
        clients = open(os.path.join(debugfs_path, subdir, "clients"), 'r')
        lines = clients.readlines()
        if len(lines) > 2:
            print "Test Environment check: other drm clients running!"
            return False

    print "Test Environment check: Succeeded."
    return True

if not os.path.exists(os.path.join(TEST_BIN_DIR, 'igt')):
    print "igt symlink not found!"
    sys.exit(0)

# Chase the piglit/bin/igt symlink to find where the tests really live.
igtTestRoot = path.join(path.realpath(path.join(TEST_BIN_DIR, 'igt')), 'tests')

igtEnvironmentOk = checkEnvironment()

profile = TestProfile()

class IGTTest(Test):
    def __init__(self, binary, arguments=[]):
        super(IGTTest, self).__init__(
            [path.join(igtTestRoot, binary)] + arguments)

    def interpret_result(self, out, returncode, results):
        if not igtEnvironmentOk:
            return out

        if returncode == 0:
            results['result'] = 'pass'
        elif returncode == 77:
            results['result'] = 'skip'
        else:
            results['result'] = 'fail'
        return out

    def run(self, env):
        if not igtEnvironmentOk:
            results = TestResult()
            results['result'] = 'fail'
            results['info'] = unicode("Test Environment isn't OK")

            return results

        return super(IGTTest, self).run(env)

def listTests(listname):
    oldDir = os.getcwd()
    try:
        os.chdir(igtTestRoot)
        proc = subprocess.Popen(
                ['make', listname ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=os.environ.copy(),
                universal_newlines=True
                )
        out, err = proc.communicate()
        returncode = proc.returncode
    finally:
        os.chdir(oldDir)

    lines = out.split('\n')
    found_header = False
    progs = ""

    for line in lines:
        if found_header:
            progs = line.split(" ")
            break

        if "TESTLIST" in line:
            found_header = True;

    return progs

singleTests = listTests("list-single-tests")

for test in singleTests:
    profile.test_list[path.join('igt', test)] = IGTTest(test)

def addSubTestCases(test):
    proc = subprocess.Popen(
            [path.join(igtTestRoot, test), '--list-subtests' ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=os.environ.copy(),
            universal_newlines=True
            )
    out, err = proc.communicate()
    returncode = proc.returncode

    subtests = out.split("\n")

    for subtest in subtests:
        if subtest == "":
            continue
        profile.test_list[path.join('igt', test, subtest)] = \
            IGTTest(test, ['--run-subtest', subtest])

multiTests = listTests("list-multi-tests")

for test in multiTests:
    addSubTestCases(test)

profile.dmesg = True
