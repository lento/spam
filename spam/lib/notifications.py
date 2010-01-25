import orbited.start
import stomp, threading, time, sys
from stomp.exception import ConnectionClosedException, NotConnectedException
from tg import config, app_globals as G
from spam.lib.jsonify import encode as json_encode
from spam.model import User, Category
from spam.model import Project, Scene, Shot, Asset, Libgroup, Journal, Note

import logging
log = logging.getLogger(__name__)

class StompClient(object):
    def __init__(self):
        self.connection = None
    
    def _setup_config(self):
        self.ORBITED_AUTOSTART = config.get('orbited_autostart', False)
        self.ORBITED_CONFIG = config.get('orbited_config', 'orbited.cfg')

        self.TOPIC_USERS = config.get('stomp_topic_users', '/topic/users')
        self.TOPIC_GROUPS = config.get('stomp_topic_groups', '/topic/groups')
        self.TOPIC_CATEGORIES = config.get('stomp_topic_categories',
                                           '/topic/categories')
        self.TOPIC_PROJECTS = config.get('stomp_topic_projects',
                                         '/topic/projects')
        self.TOPIC_SCENES = config.get('stomp_topic_scenes', '/topic/scenes')
        self.TOPIC_SHOTS = config.get('stomp_topic_shots', '/topic/shots')
        self.TOPIC_ASSETS = config.get('stomp_topic_assets', '/topic/assets')
        self.TOPIC_LIBGROUPS = config.get('stomp_topic_libgroups',
                                          '/topic/libgroups')
        self.TOPIC_PROJECT_ADMINS = config.get('stomp_topic_project_admins',
                                               '/topic/project_admins')
        self.TOPIC_PROJECT_SUPERVISORS = config.get(
                                            'stomp_topic_project_supervisors',
                                            '/topic/project_supervisors')
        self.TOPIC_PROJECT_ARTISTS = config.get('stomp_topic_project_artists',
                                                '/topic/project_artists')
        self.TOPIC_JOURNAL = config.get('stomp_topic_journal', '/topic/journal')
        self.TOPIC_NOTES = config.get('stomp_topic_notesl', '/topic/notes')

        self.topics = {User: self.TOPIC_USERS,
                       Category: self.TOPIC_CATEGORIES,
                       Project: self.TOPIC_PROJECTS,
                       Scene: self.TOPIC_SCENES,
                       Shot: self.TOPIC_SHOTS,
                       Asset: self.TOPIC_ASSETS,
                       Libgroup: self.TOPIC_LIBGROUPS,
                       Journal: self.TOPIC_JOURNAL,
                       Note: self.TOPIC_NOTES,
                      }
    
    # adapted from orbited start.py main()
    def _start_orbited(self):
        log.debug('_start_orbited()')
        oldargv = sys.argv[:]
        sys.argv[1:] = ['--config', self.ORBITED_CONFIG]
        orbited.start.main()
        sys.argv = oldargv

    def _start_connection(self):
        log.debug('_start_connection()')
        self.connection = stomp.Connection()
        self.connection.start()
        self.connection.connect()

    def connect(self):
        """start the connection in a non-blocking thread"""
        self._setup_config()
        if self.ORBITED_AUTOSTART in [True, 'True', 'true']:
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
        if not destination:
            destination = self.topics.get(type(instance), None)
        content = dict(ob=instance, update_type=update_type)
        content.update(kwargs)
        msg = json_encode(content)
        
        try:
            self.connection.send(msg, destination=destination)
        except (AttributeError, ConnectionClosedException,
                                                        NotConnectedException):
            log.debug('STOMP not connected')

    def ancestors(self, instance, update_type="updated", **kwargs):
        """Recursively send notifications to an instance's ancestors.
        
        This is mainly useful when updating the status of an asset, so that the
        status of its containers can be updated too."""
        if hasattr(instance, 'parent') and instance.parent is not None:
            self.send(instance.parent, update_type, **kwargs)
            self.ancestors(instance.parent)


notify = StompClient()

