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

from contextlib import contextmanager
import re
from diffoscope import logger, tool_required
from diffoscope.comparators.binary import File, needs_content
from diffoscope.difference import Difference
from diffoscope.comparators.utils import Command


class UimageMetadata(Command):
    @tool_required('mkimage')
    def cmdline(self):
        return ['mkimage', '-l', self.path]


class UimageFile(File):
    RE_FILE_TYPE = re.compile(r'^u-boot legacy uImage')

    @staticmethod
    def recognizes(file):
        return UimageFile.RE_FILE_TYPE.match(file.magic_file_type)

    def header_data_crc(self):
        match = re.match(r'.*(Header CRC: \w+, Data CRC: \w+)',
            self.magic_file_type)
        if match is None:
            return None
        return match.groups()[0].replace(', ', '\n')

    @needs_content
    def compare_details(self, other, source=None):
        differences = []
        differences.append(
            Difference.from_command(UimageMetadata, self.path, other.path))
        differences.append(Difference.from_text(self.header_data_crc(),
                                                other.header_data_crc(),
                                                self.path,
                                                other.path,
                                                source="uImage Header Checksums"))
        return differences

