from apps.core.enums import FileType

# Write your functions here


def get_type_path(type: str, user_id: int) -> str:
    if type == FileType.PROFILE:
        return f"PROFILES/user_{user_id}/"
    elif type == FileType.WAREHOUSE_IMAGES:
        return f"WAREHOUSE/user_{user_id}"
