from triduum_resource.cross_app import serializers
from datetime import datetime
import jwt

def jwt_response_payload_handler(token, user=None, request=None):
    payload = jwt.decode(token, verify=False, algorithms=['HS256'])
    return {
        'key': token,
        'user': serializers.UserSerializer(user, context={'request': request}).data,
        'expires': datetime.fromtimestamp(payload['exp']).isoformat()
    }