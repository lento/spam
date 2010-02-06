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
"""Setup the SPAM application"""

import logging
from tg import app_globals
from spam.config.environment import load_environment

__all__ = ['setup_app']

log = logging.getLogger(__name__)

from dirs import setup_dirs
from schema import setup_schema
from bootstrap import bootstrap

def setup_app(command, conf, vars):
    """Place any commands to setup SPAM here"""
    load_environment(conf.global_conf, conf.local_conf)
    setup_dirs(command, conf, vars)
    setup_schema(command, conf, vars)
    bootstrap(command, conf, vars)
