import asyncio

from tapvalidator.models.tap_service import TAPService
from tapvalidator.models.status import Status
from tapvalidator.models.query import Query
from tapvalidator.models.result import ValidationResult
from tapvalidator.services.tap_query_generator import QueryGenerator
from tapvalidator.services.tap_query import QueryRunner
from tapvalidator.logger.logger import logger, query_validation_logger
from tapvalidator.comparators.columns import ColumnComparator
from tapvalidator.settings import settings


class TableValidator:
    """
    Table Validator implementation.
    Implements validation methods to validate the Tables of a TAP Service
    """

    def __init__(self, tap_service: TAPService, fullscan: bool = False):
        self.tap_service = tap_service
        self.fullscan = fullscan
        self.semaphore = asyncio.Semaphore(settings.max_parallel_tasks)

    @staticmethod
    def handle_errors(q: Query, validation_result: ValidationResult):
        """Handles the errors of a Query validation

        Args:
            q (Query): The Query that is being validated
            validation_result (ValidationResult): The Validation Result object
        """
        if q.status in (Status.FAIL, Status.TRUNCATED):
            error_message = f"Query Failed [{q.query_text}]"
            validation_result.failures.append(q)
            validation_result.status = q.status
            logger.error(
                error_message,
                query=q.query_text,
                schema=q.schema_name,
            )
        elif q.status is Status.COLUMN_VALIDATION_FAIL:
            error_message = (
                f"Validation Failed [{q.query_text}] [Column Validation Error]"
            )
            validation_result.status = Status.COLUMN_VALIDATION_FAIL
            validation_result.failures.append(q)
            logger.error(
                error_message,
                query=q.query_text,
                schema=q.schema_name,
                error=Status.COLUMN_VALIDATION_FAIL,
            )
        else:
            if validation_result.status is Status.PENDING:
                validation_result.status = Status.SUCCESS

    async def validate_columns(self, q: Query, validation_result: ValidationResult):
        """Validates that the columns of a query are correct
        Args:
            q (Query): The Query to validate
            validation_result (ValidationResult): The result of the validation
        """
        expected_columns_query = QueryGenerator.get_columns_query(
            tap_service=self.tap_service,
            table_name=q.table_name,
            schema_name=q.schema_name,
        )
        QueryRunner.run_sync_query(expected_columns_query)
        column_validation_success = ColumnComparator.compare(
            actual=q.result,
            expected=expected_columns_query.result,
        )

        if column_validation_success:
            validation_result.status = Status.SUCCESS
        else:
            validation_result.status = Status.COLUMN_VALIDATION_FAIL

    @query_validation_logger
    async def validate_single_query(
        self, q: Query, validation_result: ValidationResult
    ) -> ValidationResult:
        """Validates a single Query to a TAP Service
        Args:
            q (Query): The Query to validate
            validation_result (ValidationResult): The Validation Result object
        Returns:
            ValidationResult: The result of the validation
        """
        QueryRunner.run_sync_query(q)
        if q.status is Status.SUCCESS:
            await self.validate_columns(q, validation_result)
        TableValidator.handle_errors(q, validation_result)
        return validation_result

    async def validate_query_async(
        self, query: Query, tasks: list, validation_result: ValidationResult
    ):
        """Validate a query asynchronously

        Args:
            query (Query): Query to validate
            tasks (list): List of tasks
            validation_result (ValidationResult): The validation result object
        """
        async with self.semaphore:
            # Run the query asynchronously
            task = self.validate_single_query(query, validation_result)
            tasks.append(task)

    async def validate(self) -> ValidationResult:
        """Validate the Tables of a TAP Service

        Returns:
            ValidationResult: The Validation Result object
        """

        tasks = []
        validation_result = ValidationResult()

        query_gen = QueryGenerator.generate_queries(self.tap_service, self.fullscan)
        queries = [query for query in query_gen]

        # Create a list of tasks to be awaited
        await asyncio.gather(
            *[
                self.validate_query_async(query, tasks, validation_result)
                for query in queries
            ]
        )

        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for res in results:
            if res.status is not Status.SUCCESS:
                validation_result.status = res.status
        return validation_result
