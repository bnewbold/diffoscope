# -*- coding: utf-8 -*-
#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2014-2015 Jérémy Bobbio <lunar@debian.org>
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
import re
import subprocess
import diffoscope.comparators
from diffoscope.comparators.binary import File, needs_content
from diffoscope.comparators.utils import Archive, get_compressed_content_name, NO_COMMENT
from diffoscope import logger, tool_required


class Bzip2Container(Archive):
    @property
    def path(self):
        return self._path

    def open_archive(self, path):
        self._path = path
        return self

    def close_archive(self):
        self._path = None

    def get_members(self):
        return {'bzip2-content': self.get_member(self.get_member_names()[0])}

    def get_member_names(self):
        return [get_compressed_content_name(self.path, '.bz2')]

    @tool_required('bzip2')
    def extract(self, member_name, dest_dir):
        dest_path = os.path.join(dest_dir, member_name)
        logger.debug('bzip2 extracting to %s', dest_path)
        with open(dest_path, 'wb') as fp:
            subprocess.check_call(
                ["bzip2", "--decompress", "--stdout", self.path],
                shell=False, stdout=fp, stderr=None)
        return dest_path


class Bzip2File(File):
    RE_FILE_TYPE = re.compile(r'^bzip2 compressed data\b')

    @staticmethod
    def recognizes(file):
        return Bzip2File.RE_FILE_TYPE.match(file.magic_file_type)

    @needs_content
    def compare_details(self, other, source=None):
        with Bzip2Container(self).open() as my_container, \
             Bzip2Container(other).open() as other_container:
            return my_container.compare(other_container)
