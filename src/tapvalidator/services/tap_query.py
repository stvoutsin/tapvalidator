import time
import asyncio
from dramatiq.results.errors import ResultTimeout, ResultMissing  # type: ignore
from tapvalidator.models.result import VOTable, Result
from tapvalidator.models.query import Query
from tapvalidator.models.status import Status
from tapvalidator.tasks import run_sync_query_task
from tapvalidator.models.query import QueryTask
from tapvalidator.logger.logger import logger
from tapvalidator.settings import settings

__all__ = ["QueryRunner"]


class QueryRunner:
    """Query Runner Service
    Handles running a TAP query"""

    def __init__(self):
        pass

    @staticmethod
    async def send_query(query: Query):
        """Sends out a query to the run_sync_query task of the dramatiq tasks

        Args:
            query (Query): The TAP query to be executed.
        Returns:
            QueryTask: The query task
        """
        if not query:
            raise ValueError("No query provided")
        logger.info(
            f"Sending query to [{query.table_name}]",
            table=query.table_name,
            query=query.query_text,
        )

        task = run_sync_query_task.send(
            query_text=query.query_text,
            tap_service_url=query.tap_service.endpoints.synchronous,
        )
        return QueryTask(query, task)

    @staticmethod
    async def get_result(query_task: QueryTask, block=False) -> VOTable | Result:
        """Get the result of a query task, as a VOTable

        Args:
            query_task (QueryTask): The Query Task
            block (bool): Whether to get as a blocking call or not

        Returns:
            VOtable | Result: The VOTable or Result object
        """
        start_time = time.time()
        timeout = settings.http_timeout
        query_error = None
        query_votable = VOTable(data="")

        while True:
            try:
                result = query_task.task.get_result(block=block, timeout=timeout)
                query_votable = VOTable(data=result)
                break  # Exit the loop if the result is obtained successfully
            except ResultTimeout:
                elapsed_time = time.time() - start_time
                if block and timeout is not None and elapsed_time >= timeout:
                    logger.warning(
                        "Timeout waiting for query result",
                        table=query_task.query.table_name,
                        query=query_task.query.query_text,
                    )
                    query_error = Result(
                        data="",
                        status=Status.FAIL,
                        messages=["Timeout waiting for query result"],
                    )
                    break  # Exit the loop on timeout
                else:
                    await asyncio.sleep(1)
            except ResultMissing:
                await asyncio.sleep(1)

        query_result = query_votable if not query_error else query_error
        query_task.query.result = query_result
        query = query_task.query
        logger.info(
            f"Query completed [{query.table_name}] [{query.status}]",
            table=query.table_name,
            query=query.query_text,
        )

        return query_result
