from tapvalidator.constants.database_engines import DatabaseEngine

__all__ = ["MSSQL_TO_VOTABLE", "convert_type"]

"""Define the mapping of datatypes in MSSQL to their VOTable equivalent
"""
MSSQL_TO_VOTABLE = {
    "CHAR": "char",
    "INTEGER": "int",
    "REAL": "float",
    "BIGINT": "long",
    "SMALLINT": "short",
    "FLOAT": "float",
    "BINARY": "char",
    "VARBINARY": "char",
    "CLOB": "char",
    "TIMESTAMP": "char",
    "VARCHAR": "char",
    "DOUBLE": "float",
    "*": "char",
}


def convert_type(db: DatabaseEngine, field_type: str) -> str:
    """Convert a field type, passed in as a string, to its
    equivalent type in VO Data Type

    Args:
        db (DatabaseEngine): The Database Engine we are converting from
        field_type (str): The field to convert

    Returns:
        str: The equivalent VO data type
    """
    if db is DatabaseEngine.MSSQL:
        return MSSQL_TO_VOTABLE[field_type]
    else:
        return field_type
