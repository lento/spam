import json

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, '__json__'):
            return obj.__json__()
        return json.JSONEncoder.default(self, obj)

custom_encoder = CustomEncoder()

def jsonify(obj):
    return custom_encoder.encode(obj)
