import asyncio
from typing import List

from tapvalidator.models.tap_service import TAPService
from tapvalidator.models.status import Status
from tapvalidator.models.query import Query
from tapvalidator.models.result import TableValidationResult
from tapvalidator.services.tap_query_generator import QueryGenerator
from tapvalidator.services.tap_query import QueryRunner
from tapvalidator.logger.logger import logger
from tapvalidator.comparators.columns import ColumnComparator
from tapvalidator.settings import settings
from tapvalidator.validators.protocol import Validator


class TableValidator(Validator):
    """
    Table Validator implementation.
    Implements validation methods to validate the Tables of a TAP Service
    """

    def __init__(self, tap_service: TAPService, fullscan: bool = False):
        self.tap_service = tap_service
        self.fullscan = fullscan
        self.semaphore = asyncio.Semaphore(settings.max_parallel_tasks)

    @staticmethod
    async def handle_errors(query: Query, validation_result: TableValidationResult):
        """Handles the errors of a Query validation

        Args:
            query (Query): The Query that is being validated
            validation_result (TableValidationResult): The Validation Result object
        """
        if query.status in (Status.FAIL, Status.TRUNCATED):
            error_message = f"Query Failed [{query.query_text}]"
            validation_result.failures.append(query)
            validation_result.status = query.status

            logger.error(
                error_message,
                query=query.query_text,
                schema=query.schema_name,
            )
        elif query.status is Status.COLUMN_VALIDATION_FAIL:
            error_message = (
                f"Validation Failed [{query.query_text}] [Column Validation Error]"
            )
            validation_result.status = Status.COLUMN_VALIDATION_FAIL
            validation_result.failures.append(query)
            logger.error(
                error_message,
                query=query.query_text,
                schema=query.schema_name,
                error=Status.COLUMN_VALIDATION_FAIL,
            )
        else:
            if validation_result.status is Status.PENDING:
                validation_result.status = Status.SUCCESS

    async def validate_columns(self, q: Query):
        """Validates that the columns of a query are correct
        Args:
            q (Query): The Query to validate
        """
        expected_columns_query = QueryGenerator.get_columns_query(
            tap_service=self.tap_service,
            table_name=q.table_name,
            schema_name=q.schema_name,
        )
        query_task = await QueryRunner.send_query(expected_columns_query)
        await QueryRunner.get_result(query_task)

        column_validation_success = ColumnComparator.compare(
            actual=q.result,
            expected=expected_columns_query.result,
        )

        if not column_validation_success:
            q.update_status(Status.COLUMN_VALIDATION_FAIL)

    # Define a function to send tasks in parallel
    @staticmethod
    async def send_queries_parallel(queries: List[Query]):
        """Send a list of queries in Parallel

        Args:
            queries (List[Query]): The list of queries
        """

        semaphore = asyncio.Semaphore(settings.max_parallel_tasks)

        async def send_query_with_semaphore(query):
            async with semaphore:
                return await QueryRunner.send_query(query)

        tasks = [send_query_with_semaphore(query) for query in queries]
        results = await asyncio.gather(*tasks)
        [await QueryRunner.get_result(task) for task in results]

    async def validate(self) -> TableValidationResult:
        """Validate the Tables of a TAP Service

        Returns:
            ValidationResult: The Validation Result object
        """

        validation_result = TableValidationResult(status=Status.SUCCESS)
        query_gen = QueryGenerator.generate_queries(self.tap_service, self.fullscan)
        queries = [query async for query in query_gen]

        await self.send_queries_parallel(queries)
        for query in queries:
            await self.handle_errors(query=query, validation_result=validation_result)

        return validation_result
