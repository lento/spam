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
"""STOMP notifications."""

import threading, time, sys
from tg import config, app_globals as G
from spam.lib.jsonify import encode as json_encode
from spam.model import User, Category, Journal, Note, Tag
from spam.model import Project, Scene, Shot, Asset, Libgroup

import logging
log = logging.getLogger(__name__)

TOPIC_USERS = config.get('topic_users', 'users')
TOPIC_GROUPS = config.get('topic_groups', 'groups')
TOPIC_CATEGORIES = config.get('topic_categories', 'categories')
TOPIC_PROJECTS_ACTIVE = config.get('topic_projects_active', 'projects_active')
TOPIC_PROJECTS_ARCHIVED = config.get('topic_projects_archived',
    'projects_archived')
TOPIC_SCENES = config.get('topic_scenes', 'scenes')
TOPIC_SHOTS = config.get('topic_shots', 'shots')
TOPIC_ASSETS = config.get('topic_assets', 'assets')
TOPIC_LIBGROUPS = config.get('topic_libgroups', 'libgroups')
TOPIC_PROJECT_STRUCTURE = config.get('topic_project_structure',
    'projects_structure')
TOPIC_PROJECT_ADMINS = config.get('topic_project_admins', 'project_admins')
TOPIC_PROJECT_SUPERVISORS = config.get('topic_project_supervisors',
    'project_supervisors')
TOPIC_PROJECT_ARTISTS = config.get('topic_project_artists', 'project_artists')
TOPIC_JOURNAL = config.get('topic_journal', 'journal')
TOPIC_NOTES = config.get('topic_notes', 'notes')
TOPIC_TAGS = config.get('topic_tags', 'tags')

TOPICS = {User: TOPIC_USERS,
          Category: TOPIC_CATEGORIES,
          Project: TOPIC_PROJECTS_ACTIVE,
          Scene: TOPIC_SCENES,
          Shot: TOPIC_SHOTS,
          Asset: TOPIC_ASSETS,
          Libgroup: TOPIC_LIBGROUPS,
          Journal: TOPIC_JOURNAL,
          Note: TOPIC_NOTES,
          Tag: TOPIC_TAGS,
         }


class DummyClient(object):
    def send(self, *args, **kw):
        pass


notify = DummyClient()

