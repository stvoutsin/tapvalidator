from dataclasses import dataclass
from tapvalidator.models.tap_service import TAPService
from tapvalidator.models.status import Status
from tapvalidator.models.result import Result, VOTable


__all__ = ["Query"]


@dataclass
class Query:
    """Query class, represents a TAP Query to a TAP Service

    Attributes:
        query_text (str): The query text as string (default "")
        schema_name (str): The schema_name (i.e. database in MSSQL) (default "")
        table_name (str): The table_name used in the query (default "")
        tap_service (TAPService): The TAPService object being queried (default None)
        result (Result): The Result object for this query (default None)
    """

    query_text: str = ""
    schema_name: str = ""
    table_name: str = ""
    tap_service: TAPService = None
    result: Result | VOTable | None = None

    @property
    def status(self):
        """
        Get the Status of the query
        Returns:
            Status: A Status object
        """
        return self.result.status if self.result else Status.PENDING
