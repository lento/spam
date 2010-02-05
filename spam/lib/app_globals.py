# -*- coding: utf-8 -*-
#
# SPAM Spark Project & Asset Manager
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.
#
# Original Copyright (c) 2010, Lorenzo Pierfederici <lpierfederici@gmail.com>
# Contributor(s): 
#
"""The application's Globals object"""

import re
from tg import config

__all__ = ['Globals']


class Globals(object):
    """Container for objects available throughout the life of the application.

    One instance of Globals is created during application initialization and
    is available during requests via the 'app_globals' variable.
    """

    def __init__(self):
        """Initialize global variables."""
        self.REPOSITORY = config.get('repository', '/var/lib/spam/repo')
        self.PREVIEWS = config.get('previews_dir', '.previews')
        self.SCENES = config.get('default_scenes_dir', 'scenes')
        self.LIBRARY = config.get('default_library_dir', 'library')
        self.DEFAULT_PROJ_DIRS = [self.SCENES, self.LIBRARY, self.PREVIEWS]
        self.ADDITIONAL_PROJ_DIRS = config.get('additional_proj_dirs', '').split()
        self.DEFAULT_PROJ_DIRS.extend(self.ADDITIONAL_PROJ_DIRS)
        self.UPLOAD = config.get('upload_dir', '/var/lib/spam/upload')

        self.ORBITED_AUTOSTART = config.get('orbited_autostart', False)
        self.ORBITED_CONFIG = config.get('orbited_config', 'orbited.cfg')

        self.pattern_name = re.compile('^[a-zA-Z0-9_\-]+$')
        self.pattern_file = re.compile('^[a-zA-Z0-9_\-]+\.[a-zA-Z0-9]+$')
        self.pattern_seq = re.compile('^[a-zA-Z0-9_\-]+\.#\.[a-zA-Z0-9]+$')
        self.pattern_tags = re.compile('^([a-zA-Z0-9_\-]+(, )?)+$')


