import pytest

from tapvalidator.models.tap_service import TAPService
from tapvalidator.models.query import Query
from tapvalidator.models.result import Result
from tapvalidator.models.status import Status
from tapvalidator.services.tap_query import QueryRunner
from unittest.mock import Mock, patch


@pytest.fixture
def mock_runnner():
    mock = Mock()
    mock.send_query.return_value = "Test"
    return mock


class TestQuery:
    #  Query object can be created with required attributes
    def test_create_query_with_required_attributes(self):
        tap_service = TAPService("http://example.com")
        query = Query("SELECT * FROM table", "schema", "table", tap_service)

        assert query.query_text == "SELECT * FROM table"
        assert query.schema_name == "schema"
        assert query.table_name == "table"
        assert query.tap_service == tap_service
        assert query.result is None

    #  Query object has a status property that returns the status of the query
    def test_query_status_property(self):
        tap_service = TAPService("http://example.com")
        query = Query("SELECT * FROM table", "schema", "table", tap_service)
        assert query.status == Status.PENDING

    #  Query object can be executed and returns a Result object
    def test_query_and_return_result(self):
        tap_service = TAPService("http://example.com")
        query = Query("SELECT * FROM table", "schema", "table", tap_service)
        query.result = Result(
            data="",
        )
        result = query.result

        assert isinstance(result, Result)

    #  Query object can be created with a Result object
    def test_create_query_with_result_object(self):
        tap_service = TAPService("http://example.com")
        result = Result("data", Status.SUCCESS, ["message"])
        query = Query("SELECT * FROM table", "schema", "table", tap_service, result)

        assert query.result == result

    #  Query object can be created without a Result object
    def test_create_query_without_result_object(self):
        tap_service = TAPService("http://example.com")
        query = Query("SELECT * FROM table", "schema", "table", tap_service)
        assert query.result is None

    #  Query object can be executed with an invalid query_text
    @pytest.mark.asyncio
    async def test_execute_query(self):
        with patch(
            "tapvalidator.services.tap_query.QueryRunner.send_query"
        ) as mock_runnner:
            mock_runnner.return_value = None

            tap_service = TAPService("http://example.com")
            query = Query("SELECT *", "schema", "table", tap_service)
            await QueryRunner.send_query(query)
            assert query.result is None
