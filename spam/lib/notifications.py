import stomp, threading
from stomp.exception import ConnectionClosedException, NotConnectedException
from tg import config
from spam.lib.jsonify import encode as json_encode
from spam.model import User, AssetCategory
from spam.model import Project, Scene, Shot, Asset, LibraryGroup

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


class StompClient(object):
    def __init__(self):
        self.connection = None
        self.topics = {User: TOPIC_USERS,
                       AssetCategory: TOPIC_CATEGORIES,
                       Project: TOPIC_PROJECTS,
                       Scene: TOPIC_SCENES,
                       Shot: TOPIC_SHOTS,
                       Asset: TOPIC_ASSETS,
                       LibraryGroup: TOPIC_LIBGROUPS,
                      }
        self.connect()
    
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


notify = StompClient()
