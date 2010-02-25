# -*- coding: utf-8 -*-
#
# This file is part of SPAM (Spark Project & Asset Manager).
#
# SPAM is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPAM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SPAM.  If not, see <http://www.gnu.org/licenses/>.
#
# Original Copyright (c) 2010, Lorenzo Pierfederici <lpierfederici@gmail.com>
# Contributor(s): 
#
"""Setup the SPAM directories"""

import os
from tg import config

import logging
log = logging.getLogger(__name__)


def setup_dirs(command, conf, vars):
    """Commands for the first-time setup of SPAM directories."""
    for name in ['db_dir', 'repository', 'upload_dir']:
        d = config.get(name, None)
        if d:
            try:
                os.makedirs(d)
            except OSError as error:
                if error.errno==17:
                    log.debug('directory "%s" already exists' % d)
                else:
                    log.debug('cannot create directory "%s"' % d)
                    raise

