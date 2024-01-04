from tapvalidator.models.result import VOTable
from tapvalidator.models.query import Query
from tapvalidator.tasks import run_sync_query_task

__all__ = ["QueryRunner"]


class QueryRunner:
    """Query Runner Service
    Handles running a TAP query"""

    def __init__(self):
        pass

    @staticmethod
    def run_sync_query(query: Query) -> VOTable:
        """
        Fetches a VOTable result for a given SQL query from an IVOA TAP service.
        Modifies the query, to set its Result as well as returning the result

        Args:
            query (Query): The TAP query to be executed.

        Returns:
            VOTable: The parsed VOTable result.
        """
        if not query:
            raise ValueError("No query provided")

        task = run_sync_query_task.send(
            query_text=query.query_text,
            tap_service_url=query.tap_service.endpoints.synchronous,
        )
        task_res = task.get_result(block=True, timeout=None)
        votable = VOTable(data=task_res)
        query.result = votable
        return votable
