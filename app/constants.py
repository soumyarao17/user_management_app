from django.db import models


class UserStatus(models.TextChoices):
    ACTIVATED = "ACTIVATED", "ACTIVATED"
    INIT = "INIT", "INIT"
    BLOCKED = "BLOCKED", "BLOCKED"


class RoleChoices(models.TextChoices):
    ADMIN = "ADMIN", "ADMIN"
    USER = "USER", "USER"


class AccessLevels(models.TextChoices):
    READ = "READ", "READ"
    WRITE = "WRITE", "WRITE"
    UPDATE = "UPDATE", "UPDATE"
    DELETE = "DELETE", "DELETE"


class Resources(models.TextChoices):
    TASK = "TASK", "TASK"
    NOTE = "NOTE", "NOTE"


ACCESS_LEVELS_CHOICES = [
    (access, access) for access in
    [
        AccessLevels.READ,
        AccessLevels.WRITE,
        AccessLevels.UPDATE,
        AccessLevels.DELETE
    ]
]

USER_STATUS_CHOICES = [
    (status, status) for status in
    [
        UserStatus.ACTIVATED,
        UserStatus.INIT,
        UserStatus.BLOCKED,
    ]
]

ROLE_CHOICES = [
    (role, role) for role in
    [
        RoleChoices.ADMIN,
        RoleChoices.USER,
    ]
]

RESOURCES = [Resources.NOTE, Resources.TASK]

