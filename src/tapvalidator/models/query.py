from dataclasses import dataclass, field
from tapvalidator.models.tap_service import TAPService
from tapvalidator.models.status import Status
from tapvalidator.models.result import VOTable


__all__ = ["Query"]


@dataclass
class Query:
    """Query class, represents a TAP Query to a TAP Service

    Attributes:
        query_text (str): The query text as string (default "")
        schema_name (str): The schema_name (i.e. database in MSSQL) (default "")
        table_name (str): The table_name used in the query (default "")
        tap_service (TAPService): The TAPService object being queried (default None)
        result (VOTable): The VOTable object for this query (default None)
    """

    query_text: str = ""
    schema_name: str = ""
    table_name: str = ""
    tap_service: TAPService = field(default_factory=TAPService)
    result: VOTable | None = None

    def update_status(self, status: Status):
        """Update the Status of the query
        Args:
            status (Status(: A Status object
        """
        if self.result:
            self.result.status = status

    @property
    def status(self):
        """
        Get the Status of the query
        Returns:
            Status: A Status object
        """
        return self.result.status if self.result else Status.PENDING
