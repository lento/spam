# -*- coding: utf-8 -*-
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

        self.pattern_name = re.compile('^[a-zA-Z0-9_\-]+$')
        self.pattern_file = re.compile('^[a-zA-Z0-9_\-]+\.[a-zA-Z0-9]+$')
        self.pattern_seq = re.compile('^[a-zA-Z0-9_\-]+\.#\.[a-zA-Z0-9]+$')
        self.pattern_tags = re.compile('^([a-zA-Z0-9_\-]+(, )?)+$')


