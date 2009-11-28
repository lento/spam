# -*- coding: utf-8 -*-
import re
from tg import config

REPOSITORY = config.get('repository', '/var/lib/spam/repo')
PREVIEWS = config.get('previews_dir', '.previews')
SCENES = config.get('default_scenes_dir', 'scenes')
LIBRARY = config.get('default_library_dir', 'library')
ADDITIONAL_PROJ_DIRS = config.get('additional_proj_dirs', '').split()
DEFAULT_PROJ_DIRS = [SCENES, LIBRARY, PREVIEWS] + ADDITIONAL_PROJ_DIRS

pattern_name = re.compile('^[a-zA-Z0-9_\-]+$')


