import pytest
from tapvalidator.models.status import Status


class TestStatus:
    #  Status object can be created with each possible Status value
    def test_create_status_with_each_possible_value(self):
        for status in Status:
            assert isinstance(status, Status)

    #  Status object can be compared with another Status object with the same value
    def test_compare_status_with_same_value(self):
        status1 = Status.SUCCESS
        status2 = Status.SUCCESS

        assert status1 == status2

    #  Status object can be converted to a string
    def test_convert_status_to_string(self):
        status = Status.SUCCESS

        assert str(status) == "SUCCESS"

    #  Status object can be compared with another object that is not a Status object
    def test_compare_status_with_non_status_object(self):
        status = Status.SUCCESS

        assert status != "SUCCESS"

    #  Status object can be created with a value that is not a string
    def test_create_status_with_non_string_value(self):
        value = 123

        with pytest.raises(ValueError):
            Status(value)

    #  Status object can be created with a value that is not a valid Status value
    def test_create_status_with_invalid_value(self):
        value = "INVALID"

        with pytest.raises(ValueError):
            Status(value)
