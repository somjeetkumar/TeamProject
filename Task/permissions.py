from rest_framework.exceptions import PermissionDenied

PERMISSIONS = {
    "Organization": {
        "create": ["owner"],
        "view": ["owner", "admin", "member"],
        "update": ["owner"],
        "delete": ["owner"],
    },
    "OrganizationMembership": {
        "view": ["owner", "admin", "member"],
        "create": ["owner", "admin"],
        "update": ["owner", "admin"],
        "delete": ["owner", "admin"],
    },
    "Team": {
        "create": ["owner", "admin"],
        "view": ["owner", "admin", "member"],
        "update": ["owner", "admin"],
        "delete": ["owner", "admin"],
    },
    "TeamMembership": {
        "view": ["owner", "admin"],
        "create": ["owner", "admin"],
        "delete": ["owner", "admin"],
    },
    "Project": {
        "create": ["owner", "admin"],
        "view": ["owner", "admin", "member"],
        "update": ["owner", "admin"],
        "delete": ["owner", "admin"],
    },
    "Task": {
        "view": ["owner", "admin", "member"],
        "create": ["owner", "admin", "member"],
        "update": ["owner", "admin", "member"],
        "delete": ["owner", "admin", "member"],
    },
        "Comment": {
    "view": ["owner", "admin", "member"],
    "create": ["owner", "admin", "member"],
    "update": ["owner", "admin", "member"],
    "delete": ["owner", "admin", "member"],
},
}


def check_permission(user, organization, model, action):
    try:
        membership = organization.memberships.get(user=user)
    except organization.memberships.model.DoesNotExist:
        raise PermissionDenied(
            "You are not a member of this organization."
        )

    allowed_roles = PERMISSIONS[model][action]

    if membership.role not in allowed_roles:
        raise PermissionDenied(
            "You do not have permission to perform this action."
        )

    return membership
