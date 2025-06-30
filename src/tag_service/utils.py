from uuid import UUID


def is_uuid(value: str) -> bool:
    """
    Check if the given string is a valid UUID.

    Args:
        value (str): The string to check.

    Returns:
        bool: True if the string is a valid UUID, False otherwise.
    """
    try:
        UUID(value)
        return True
    except ValueError:
        return False
