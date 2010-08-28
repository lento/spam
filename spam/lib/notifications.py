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

import orbited.start
import stomp, threading, time, sys
from stomp.exception import ConnectionClosedException, NotConnectedException
from tg import config, app_globals as G
from spam.lib.jsonify import encode as json_encode
from spam.model import User, Category, Journal, Note, Tag
from spam.model import Project, Scene, Shot, Asset, Libgroup

import logging
log = logging.getLogger(__name__)

ORBITED_AUTOSTART = config.get('orbited_autostart', False)
ORBITED_CONFIG = config.get('orbited_config', 'orbited.cfg')

TOPIC_USERS = config.get('stomp_topic_users', 'users')
TOPIC_GROUPS = config.get('stomp_topic_groups', 'groups')
TOPIC_CATEGORIES = config.get('stomp_topic_categories', 'categories')
TOPIC_PROJECTS_ACTIVE = config.get('stomp_topic_projects_active',
    'projects_active')
TOPIC_PROJECTS_ARCHIVED = config.get('stomp_topic_projects_archived',
    'projects_archived')
TOPIC_SCENES = config.get('stomp_topic_scenes', 'scenes')
TOPIC_SHOTS = config.get('stomp_topic_shots', 'shots')
TOPIC_ASSETS = config.get('stomp_topic_assets', 'assets')
TOPIC_LIBGROUPS = config.get('stomp_topic_libgroups', 'libgroups')
TOPIC_PROJECT_STRUCTURE = config.get('stomp_topic_project_structure',
    'projects_structure')
TOPIC_PROJECT_ADMINS = config.get('stomp_topic_project_admins',
    'project_admins')
TOPIC_PROJECT_SUPERVISORS = config.get('stomp_topic_project_supervisors',
    'project_supervisors')
TOPIC_PROJECT_ARTISTS = config.get('stomp_topic_project_artists',
    'project_artists')
TOPIC_JOURNAL = config.get('stomp_topic_journal', 'journal')
TOPIC_NOTES = config.get('stomp_topic_notesl', 'notes')
TOPIC_TAGS = config.get('stomp_topic_tags', 'tags')


class StompClient(object):
    """A client to connect to a stomp server and send messages.
    
    If the destination is not specified, messages are sent to the topic
    associated with the class of the object given as first parameter.
    StompClient can optionally start an ``Orbited`` server on the localhost."""
    def __init__(self):
        self.connection = None
        self._setup_config()
    
    def _setup_config(self):
        self.topics = {User: TOPIC_USERS,
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
    
    def _start_orbited(self):
        oldargv = sys.argv[:]
        sys.argv[1:] = ['--config', ORBITED_CONFIG]
        orbited.start.main()
        sys.argv = oldargv

    def _start_connection(self):
        self.connection = stomp.Connection()
        self.connection.start()
        self.connection.connect()

    def connect(self):
        """Start the connection in a non-blocking thread."""
        if ORBITED_AUTOSTART in [True, 'True', 'true']:
            self.thread_orbited = threading.Thread(None, self._start_orbited)
            self.thread_orbited.start()
        self.thread_connect = threading.Thread(None, self._start_connection)
        self.thread_connect.start()
    
    def send(self, instance, update_type="updated", destination=None, **kwargs):
        """Send a message to the stomp server.
        
        The message body is a json object in the form:
        {"update_type": "...", "ob": {...}}
        Update_type can be "updated", "added", "removed" or a custom string.
        If not given, "destination" will be derived from the type of "instance".
        """
        pass
#        if not destination:
#            destination = self.topics.get(type(instance), None)
#        content = dict(ob=instance, update_type=update_type)
#        content.update(kwargs)
#        msg = json_encode(content)
#        
#        try:
#            self.connection.send(msg, destination=destination)
#        except (AttributeError, ConnectionClosedException,
#                                                        NotConnectedException):
#            log.debug('STOMP not connected')

    def ancestors(self, instance, update_type="updated", **kwargs):
        """Recursively send notifications to an instance's ancestors.
        
        This is mainly useful when updating the status of an asset, so that the
        status of its containers can be updated too."""
        if hasattr(instance, 'parent') and instance.parent is not None:
            self.send(instance.parent, update_type, **kwargs)
            self.ancestors(instance.parent)


notify = StompClient()

