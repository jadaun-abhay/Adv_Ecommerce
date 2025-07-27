from enum import IntEnum

# Write your enums here


class Status(IntEnum):
    CREATED = 0
    UPDATED = 1
    DELETED = 3


class FileType(IntEnum):
    WAREHOUSE_IMAGES = 0
    PROFILE = 1
