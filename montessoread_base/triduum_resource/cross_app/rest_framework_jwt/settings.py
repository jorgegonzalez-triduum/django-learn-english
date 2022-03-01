import datetime

JWT_AUTH = {
    'JWT_RESPONSE_PAYLOAD_HANDLER':
    'triduum_resource.cross_app.rest_framework_jwt.payloads.jwt_response_payload_handler',
    'JWT_AUTH_HEADER_PREFIX': 'key',
    'JWT_ALLOW_REFRESH': True,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=1),
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=1),
}
