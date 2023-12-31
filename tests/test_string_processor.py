from tapvalidator.utility.string_processor import StringProcessor
from tapvalidator.models.tap_service import TAPService
from tapvalidator.models.result import ValidationResult
from tapvalidator.models.status import Status


class TestStringProcessor:
    #  Should add quotes around a keyword in a query if it is a reserved keyword
    def test_fix_keywords_with_reserved_keyword(self):
        string_processor = StringProcessor()
        table_name = "SELECT"
        fixed_table_name = string_processor.fix_keywords(table_name)
        assert fixed_table_name == '"SELECT"'

    #  Should return the original string if it is not a reserved keyword
    def test_fix_keywords_with_non_reserved_keyword(self):
        string_processor = StringProcessor()
        query = "SELECT * FROM table"
        fixed_query = string_processor.fix_keywords(query)
        assert fixed_query == "SELECT * FROM table"

    #  Should generate an alert message for a failed query with relevant logs
    def test_generate_alert_message(self):
        string_processor = StringProcessor()
        tap_service = TAPService(url="example_tap_service")
        validation_result = ValidationResult(
            messages=["Error 1", "Error 2"], status=Status.FAIL
        )
        alert_message = string_processor.generate_alert_message(
            validation_result=validation_result, tap_service=tap_service
        )
        expected_message = (
            "Notification for tap_service: [example_tap_service]\n"
            "Validation result: [FAIL]\nRelevant logs:\nError 1\nError 2\n"
        )
        assert alert_message == expected_message
