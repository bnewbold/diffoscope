# -*- coding: utf-8 -*-
#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2015 Bryan Newbold <bnewbold@robocracy.org>
#
# diffoscope is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# diffoscope is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with diffoscope.  If not, see <http://www.gnu.org/licenses/>.

import os.path
import pwd
import pytest
from diffoscope.comparators import specialize
from diffoscope.comparators.binary import FilesystemFile, NonExistingFile
from diffoscope.comparators.uimage import UimageFile
from diffoscope.config import Config
from conftest import tool_missing, try_except

# Test images were generated with:
#    mkimage -a 0x00001111 -e 0x11110000 -n "diffoscope test uImage #1" -d tests/data/binary1 binary1.uImage
#    mkimage -a 0x00002222 -e 0x22220000 -n "diffoscope test uImage #2" -d tests/data/binary2 binary2.uImage

TEST_FILE1_PATH = os.path.join(os.path.dirname(__file__), '../data/binary1.uImage')
TEST_FILE2_PATH = os.path.join(os.path.dirname(__file__), '../data/binary2.uImage')

@pytest.fixture
def uimage1():
    return specialize(FilesystemFile(TEST_FILE1_PATH))

@pytest.fixture
def uimage2():
    return specialize(FilesystemFile(TEST_FILE2_PATH))

def test_identification(uimage1):
    assert isinstance(uimage1, UimageFile)

def test_no_differences(uimage1):
    difference = uimage1.compare(uimage1)
    assert difference is None

def test_no_warnings(capfd, uimage1, uimage2):
    _ = uimage1.compare(uimage2)
    _, err = capfd.readouterr()
    assert err == ''

@pytest.fixture
def differences(uimage1, uimage2):
    return uimage1.compare(uimage2).details

@pytest.mark.skipif(tool_missing('mkimage'), reason='missing mkimage')
def test_compare_identical(uimage1):
    difference = uimage1.compare(uimage1, uimage1)
    assert difference is None

@pytest.mark.skipif(tool_missing('mkimage'), reason='missing mkimage')
def test_mkimage_list(differences):
    expected_diff = open(os.path.join(os.path.dirname(__file__), '../data/uimage_header_expected_diff')).read()
    assert differences[0].unified_diff == expected_diff

@pytest.mark.skipif(tool_missing('mkimage'), reason='missing mkimage')
def test_crcs(differences):
    expected_diff = open(os.path.join(os.path.dirname(__file__), '../data/uimage_crc_expected_diff')).read()
    assert differences[1].unified_diff == expected_diff
