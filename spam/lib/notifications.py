import stomp, threading
from stomp.exception import ConnectionClosedException, NotConnectedException
from tg import config
from spam.lib.jsonify import encode as json_encode
from spam.model import User, Category
from spam.model import Project, Scene, Shot, Asset, LibraryGroup, Journal

import logging
log = logging.getLogger(__name__)

TOPIC_USERS = config.get('stomp_topic_users', '/topic/users')
TOPIC_GROUPS = config.get('stomp_topic_groups', '/topic/groups')
TOPIC_CATEGORIES = config.get('stomp_topic_categories', '/topic/categories')
TOPIC_PROJECTS = config.get('stomp_topic_projects', '/topic/projects')
TOPIC_SCENES = config.get('stomp_topic_scenes', '/topic/scenes')
TOPIC_SHOTS = config.get('stomp_topic_shots', '/topic/shots')
TOPIC_ASSETS = config.get('stomp_topic_assets', '/topic/assets')
TOPIC_LIBGROUPS = config.get('stomp_topic_libgroups', '/topic/libgroups')
TOPIC_PROJECT_ADMINS = config.get(
                        'stomp_topic_project_admins', '/topic/project_admins')
TOPIC_PROJECT_SUPERVISORS = config.get(
                'stomp_topic_project_supervisors', '/topic/project_supervisors')
TOPIC_PROJECT_ARTISTS = config.get(
                'stomp_topic_project_artists', '/topic/project_artists')
TOPIC_JOURNAL = config.get('stomp_topic_journal', '/topic/journal')


class StompClient(object):
    def __init__(self):
        self.connection = None
        self.topics = {User: TOPIC_USERS,
                       Category: TOPIC_CATEGORIES,
                       Project: TOPIC_PROJECTS,
                       Scene: TOPIC_SCENES,
                       Shot: TOPIC_SHOTS,
                       Asset: TOPIC_ASSETS,
                       LibraryGroup: TOPIC_LIBGROUPS,
                       Journal: TOPIC_JOURNAL,
                      }
    
    def _start_connection(self):
        self.connection = stomp.Connection()
        self.connection.start()
        self.connection.connect()

    def connect(self):
        """start the connection in a non-blocking thread"""
        self.thread = threading.Thread(None, self._start_connection)
        self.thread.start()
    
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

