import pytest
from unittest.mock import patch
from tapvalidator.models.validation_config import ValidationConfiguration
from tapvalidator.models.tap_service import TAPService
from tapvalidator.tap_validator import TAPValidator
from tapvalidator.models.status import Status
from tapvalidator.models.query import Query
from tapvalidator.models.result import ValidationResult
from tapvalidator.services.alerter import AlertingStrategies, AlertStrategy
from tapvalidator.exceptions.invalid_mode import InvalidRunMode


class TestTAPValidator:
    #  can validate tables of a TAP service

    @pytest.mark.asyncio
    @patch(
        "tapvalidator.validators.table_validator.TableValidator.validate",
        return_value=ValidationResult(status=Status.SUCCESS, failures=[]),
    )
    async def test_validate_tables(self, mock_validate):
        # Create a TAPValidator instance
        config = ValidationConfiguration(
            first_service=TAPService(url="http://example.com/tap")
        )
        tap_validator = TAPValidator(config)

        # Call the validate_tables method
        await tap_validator.validate_tables(fullscan=True)
        # Assert that the TableValidator's validate method was called
        mock_validate.assert_called_once()

    @patch(
        "tapvalidator.services.alerter.AlerterService.send_alert",
        return_value=True,
    )
    def test_handle_notifications(self, mock_send_alert):
        tap_service = TAPService(url="http://tap.roe.ac.uk/osa")
        # Create a TAPValidator instance
        config = ValidationConfiguration(
            first_service=tap_service,
            alerter=AlertingStrategies[AlertStrategy.LOG],
            alert_destination="http://example.com/alert",
        )
        tap_validator = TAPValidator(config)
        q = Query(query_text="SELECT", tap_service=tap_service)
        # Create a ValidationResult instance
        validation_result = ValidationResult(failures=[q], status=Status.FAIL)

        # Call the handle_notifications method
        tap_validator.handle_notifications(validation_result)

        # Assert that the send_alert function was called
        mock_send_alert.assert_called_once()

    #  raises InvalidRunMode exception for unknown run mode
    @pytest.mark.asyncio
    async def test_invalid_run_mode(self):
        # Create a TAPValidator instance
        config = ValidationConfiguration(
            first_service=TAPService(url="http://example.com/tap")
        )
        tap_validator = TAPValidator(config)

        # Assert that an InvalidRunMode exception is raised when
        # an unknown run mode is provided
        with pytest.raises(InvalidRunMode):
            await tap_validator.run(mode="UNKNOWN_MODE")

    #  raises NotImplementedError for comparison mode without known set of queries
    @pytest.mark.asyncio
    async def test_comparison_mode_no_queries(self):
        # Create a TAPValidator instance
        config = ValidationConfiguration(
            first_service=TAPService(url="http://example.com/tap"), queries=None
        )
        tap_validator = TAPValidator(config)

        # Assert that a NotImplementedError is raised when
        # running comparison mode without known set of queries
        with pytest.raises(NotImplementedError):
            await tap_validator.run(mode="COMPARISON")
