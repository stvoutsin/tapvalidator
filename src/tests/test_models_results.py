from tapvalidator.models.status import Status
from tapvalidator.models.result import Result


class TestResult:
    #  Result object can be created with default values for all attributes
    def test_create_result_with_default_values(self):
        result = Result()

        assert result.data == ""
        assert result.status == Status.PENDING
        assert result.messages == []

    #  Result object can be created with custom values for all attributes
    def test_create_result_with_custom_values(self):
        data = "custom data"
        status = Status.SUCCESS
        messages = ["message 1", "message 2"]

        result = Result(data, status, messages)

        assert result.data == data
        assert result.status == status
        assert result.messages == messages

    #  Result object can be compared with another Result object with same data
    def test_compare_result_with_same_data_attribute(self):
        data = "same data"

        result1 = Result(data)
        result2 = Result(data)

        assert result1 == result2

    #  Result object can be created with an empty data attribute
    def test_create_result_with_empty_data_attribute(self):
        result = Result()

        assert result.data == ""

    #  Result object can be created with a non-empty data attribute
    def test_create_result_with_non_empty_data_attribute(self):
        data = "non-empty data"

        result = Result(data)

        assert result.data == data

    #  Result object can be created with a Status attribute of each possible Status
    def test_create_result_with_each_status_value(self):
        for status in Status:
            result = Result(status=status)
            assert result.status == status
