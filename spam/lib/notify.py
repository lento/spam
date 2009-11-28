import stomp
from tg import config
from spam.lib.jsonify import encode as json_encode


TOPIC_PROJECTS = config.get('stomp_topic_projects', '/topic/projects')
TOPIC_SCENES = config.get('stomp_topic_sceness', '/topic/scenes')
TOPIC_SHOTS = config.get('stomp_topic_shots', '/topic/shots')

stompconn = stomp.Connection()
stompconn.start()
stompconn.connect()

def project(project, update_type='updated'):
    """Send a message to stomp's projects topic.

    The message body is a json object in the form:
    {"update_type": "...", "ob": {...}}
    where update_type is one of: updated, added, removed, archived, activated
    """
    msg = json_encode(dict(ob=project, update_type=update_type))
    stompconn.send(msg, destination=TOPIC_PROJECTS)

def scene(scene, update_type='updated'):
    """Send a message to stomp's scenes topic.

    The message body is a json object in the form:
    {"update_type": "...", "ob": {...}}
    where update_type is one of: updated, added, removed
    """
    msg = json_encode(dict(ob=scene, update_type=update_type))
    stompconn.send(msg, destination=TOPIC_SCENES)

def shot(shot, update_type='updated'):
    """Send a message to stomp's shot topic.

    The message body is a json object in the form:
    {"update_type": "...", "ob": {...}}
    where update_type is one of: updated, added, removed
    """
    msg = json_encode(dict(ob=shot, update_type=update_type))
    stompconn.send(msg, destination=TOPIC_SHOTS)

