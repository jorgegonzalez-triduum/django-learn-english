from collections import namedtuple

# Globals of versioning
PermissionType = namedtuple(
    'PermissionType', ('section', 'funcionality'))

permission_type = PermissionType(1, 2)