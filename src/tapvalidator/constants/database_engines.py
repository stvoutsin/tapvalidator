from enum import Enum, auto

__all__ = ["DatabaseEngine", "str_to_db_engine"]


class DatabaseEngine(Enum):
    """A class for defining Database Engines"""

    MSSQL = auto()
    DEFAULT = auto()


def str_to_db_engine(dbstr: str) -> DatabaseEngine:
    """Convert a string to its equivalent DatabaseEngine Enum class value

    Args:
        dbstr (str): The Database engine string representation

    Returns:
        DatabaseEngine:  The Database engine that the string corresponds to

    """
    if dbstr == "MSSQL":
        return DatabaseEngine.MSSQL
    else:
        return DatabaseEngine.DEFAULT
