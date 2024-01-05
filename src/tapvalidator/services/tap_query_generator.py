import random
from typing import Iterator
from tapvalidator.models.query import Query
from tapvalidator.models.tap_service import TAPService
from tapvalidator.services.tap_query import QueryRunner
from tapvalidator.utility.string_processor import StringProcessor

__all__ = ["QueryGenerator"]


class QueryGenerator:
    """Query Generator class, provides a generator for getting queries for the
    validation"""

    def __init__(self):
        pass

    @staticmethod
    def generate_queries(tap_service: TAPService, fullscan: bool) -> Iterator[Query]:
        """Generator, used for fetching queries to be tested for the TAP Service
        Gets a list of TAP_SCHEMA schemas (i.e. databases), and the generator
        iterates through the list of databases and fetches a "SELECT TOP 1 * FROM
        Table" for each table if fullscan is True, otherwise just picks a random
        table from the Schema (Database)

        Args:
            tap_service (TAPService): The TAP Service
            fullscan (bool): Whether to do a full table scan

        Returns:
            Iterator[Query]: Iterator object, with iter yield type being a Query
        """

        def _get_table_query(table_obj: tuple, schema_str: str):
            """Get the table query

            Args:
                table_obj (tuple): The Table object
                schema_str (str): The schema name

            Returns:
                Query: A "Select top 1 *.." Query object for that schema_name and table
            """
            table_name = table_obj[0]
            return QueryGenerator.get_top_1_query(
                table_name=table_name, tap_service=tap_service, schema_name=schema_str
            )

        schemas_result = QueryRunner.run_sync_query(
            QueryGenerator.get_schemas_query(tap_service=tap_service)
        )
        schemas = (
            schemas_result.astropy_table.array if schemas_result.astropy_table else []
        )

        for schema in schemas:
            schema_name = schema[0]
            tables_result = QueryRunner.run_sync_query(
                QueryGenerator.get_tables_query(
                    schema_name=schema_name, tap_service=tap_service
                )
            )
            tables = (
                tables_result.astropy_table.array if tables_result.astropy_table else []
            )

            if fullscan:
                for table in tables:
                    yield _get_table_query(table, schema_str=schema_name)
            else:
                yield _get_table_query(random.choice(tables), schema_str=schema_name)

    @staticmethod
    def get_schemas_query(tap_service: TAPService) -> Query:
        """Get the schemas for a TAP Service

        Args:
            tap_service (TAPService): The TAP service

        Returns:
            Query: The query which fetches the schemas
        """
        q = "SELECT schema_name FROM TAP_SCHEMA.schemas"
        return Query(
            query_text=q,
            schema_name="TAP_SCHEMA",
            table_name="schemas",
            tap_service=tap_service,
        )

    @staticmethod
    def get_tables_query(schema_name: str, tap_service: TAPService) -> Query:
        """Get the query that can fetch the tables of a Schema in a TAP Service

        Args:
            schema_name (str): The schema name that the tables are under
            tap_service (TAPService): The TAP Service

        Returns:
            Query: The query that fetches the tables for the schema
        """
        q = (
            f"SELECT table_name FROM TAP_SCHEMA.tables "
            f"WHERE schema_name='{schema_name}'"
        )
        return Query(
            query_text=q,
            schema_name=schema_name,
            table_name="tables",
            tap_service=tap_service,
        )

    @staticmethod
    def get_top_1_query(
        table_name: str, schema_name: str, tap_service: TAPService
    ) -> Query:
        """Get a query that selects the TOP 1 * From a table

        Args:
            table_name (str): The Table name that is to be queried
            schema_name (str): The Schema that the table belongs to
            tap_service (TAPService): The TAP Service

        Returns:
            Query: The query
        """
        q = f"SELECT TOP 1 * FROM {StringProcessor.fix_keywords(table_name)}"

        return Query(
            query_text=q,
            schema_name=schema_name,
            table_name=table_name,
            tap_service=tap_service,
        )

    @staticmethod
    def get_columns_query(
        table_name: str, schema_name: str, tap_service: TAPService
    ) -> Query:
        """Get the query that will select the columns of a Table

        Args:
            table_name (str): The Table name
            schema_name (str): The Schema name
            tap_service (TAPService): The TAP Service that is being queried

        Returns:
            Query: The query that allows getting the columns for a table
        """
        q = (
            f"SELECT column_name, datatype FROM TAP_SCHEMA.columns "
            f"WHERE table_name ='{table_name}'"
        )
        return Query(
            query_text=q,
            schema_name=schema_name,
            table_name="columns",
            tap_service=tap_service,
        )
