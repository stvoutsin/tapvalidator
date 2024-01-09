"""
Module for providing TAP Validation Capabilities

Allows validating & comparing two different TAP Services, or just validating one
TAP Service For a single TAP Service, either a full TAP Validation can be run which
validates various aspects of a TAP Service, or if TABLE_VALIDATION_ONLY is the run
mode, only the Tables of a TAP Service are validated.

TABLE_VALIDATION_ONLY can be used for healthchecking a TAP Service and
its underlying SQL Database
"""
import asyncio
import click

from tapvalidator.models.status import Status
from tapvalidator.models.tap_service import TAPService
from tapvalidator.logger.logger import logger
from tapvalidator.services.tap_query import QueryRunner
from tapvalidator.models.result import ValidationResult
from tapvalidator.models.query import Query
from tapvalidator.models.run_mode import Mode as RunMode
from tapvalidator.services.alerter import AlerterResolver, AlerterService
from tapvalidator.validators.availability_validator import AvailabilityValidator
from tapvalidator.validators.capabilities_validator import CapabilitiesValidator
from tapvalidator.validators.table_validator import TableValidator
from tapvalidator.comparators.votable import VOTableComparator
from tapvalidator.validators.vosi_validator import VOSIValidator
from tapvalidator.utility.string_processor import StringProcessor
from tapvalidator.exceptions.invalid_mode import InvalidRunMode
from tapvalidator.models.validation_config import ValidationConfiguration

__all__ = ["TAPValidator"]


class TAPValidator:
    """
    TAPValidator is a class that provides capabilities for validating TAP services.
    """

    def __init__(self, config: ValidationConfiguration):
        self.config = config
        self.run_actions = {
            RunMode.COMPARISON.value: self.compare_tap_services,
            RunMode.VALIDATION.value: self.validate_tap_service,
            RunMode.TABLE_VALIDATION.value: self.validate_tables,
        }

    async def run(self, mode, **kwargs):
        """Run a TAPValidator action

        Args:
            mode (Mode): The mode of the run
                          Can be one of (COMPARISON,VALIDATION,TABLE_VALIDATION_ONLY)

        """
        if mode.upper() not in self.run_actions:
            raise InvalidRunMode(mode)
        await self.run_actions[mode.upper()](**kwargs)

    async def validate_tables(self, fullscan: bool = False):
        """
        Validate the tables of a TAP Service
        Args:
            fullscan (bool): Whether to do a full scan
        """
        validation_task = asyncio.create_task(
            TableValidator(self.config.first_service, fullscan=fullscan).validate()
        )
        result = await validation_task
        await self.handle_notifications(result)

    async def validate_tap_service(self, fullscan: bool = False):
        """
        Validate the service with a list of queries
        Args:
            fullscan (bool): Whether to do a full scan

        """
        validators = [
            TableValidator(self.config.first_service, fullscan),
            VOSIValidator(self.config.first_service),
            AvailabilityValidator(self.config.first_service),
            CapabilitiesValidator(self.config.first_service),
        ]

        for validator in validators:
            validation_task = asyncio.create_task(validator.validate())
            result = await validation_task
            await self.handle_notifications(result)

    async def handle_notifications(self, validation_result: ValidationResult):
        """Handle sending out notification if this functionality is enabled

        Args:
            validation_result (ValidationResult): Validation result for the
            notification message
        """
        if not self.config.alerter:
            return

        if validation_result.status is not Status.SUCCESS:
            msg = StringProcessor.generate_alert_message(
                validation_result=validation_result,
                tap_service=self.config.first_service,
            )

            AlerterService.send_alert(
                msg=msg,
                destination=self.config.alert_destination,
                alerter=self.config.alerter,
            )

    async def compare_tap_services(self):
        """Runs the comparison for SQL queries stored in a text file."""
        if self.config.queries:
            with open(self.config.queries, "r") as file:
                queries = file.readlines()

            for query in queries:
                q1 = Query(query_text=query, tap_service=self.config.first_service)
                qtask = await QueryRunner.send_query(query=q1)
                await QueryRunner.get_result(qtask)

                q2 = Query(query_text=query, tap_service=self.config.second_service)
                qtask = await QueryRunner.send_query(query=q1)
                await QueryRunner.get_result(qtask)

                if VOTableComparator.compare(q1.result, q2.result):
                    logger.info(f"{query} [OK]")
                else:
                    logger.error(f"{query} [OK]")
        else:
            raise NotImplementedError(
                "Can only use function with a known set of queries currently"
            )


@click.command()
@click.option("--mode", help="Mode for TAP Validator")
@click.option(
    "--tap_service", help="The URL of the main TAP service for the validation"
)
@click.option(
    "--secondary_tap_service",
    help="The URL of the second TAP service to use for the comparison",
    required=False,
    default="",
)
@click.option(
    "--slack_webhook",
    help="The Slack Webhook URL, which (optionally) an alert should be sent to",
    required=False,
    default="",
)
@click.option(
    "--queries",
    help="If specific queries are used for the comparison, provide as url or path",
    required=False,
    default="",
)
@click.option(
    "--notification_method",
    help="The notification method for the validation",
    required=False,
    default="LOG",
)
@click.option(
    "--fullscan",
    is_flag=True,
    help="Whether to perform a full table scan if running the table validation",
    required=False,
    default=False,
)
def main(
    mode: str,
    tap_service: str,
    slack_webhook: str = "",
    queries: str = "",
    fullscan: bool = False,
    notification_method: str = "LOG",
    secondary_tap_service: str = "",
):
    """TAP Validation tool, allows you to run validate that a TAP Service is
    operating as expected

    Additionally, allows comparison to be run between two TAP Services that contain
    the same dataset
    """

    notification_method = "SLACK" if slack_webhook is not None else notification_method
    config = ValidationConfiguration(
        first_service=TAPService(url=tap_service),
        second_service=TAPService(url=secondary_tap_service),
        alerter=AlerterResolver.get_alerter(notification_method),
        alert_destination=slack_webhook,
        queries=queries,
    )

    tap_validator = TAPValidator(config)
    asyncio.run(tap_validator.run(mode=mode, fullscan=fullscan))


if __name__ == "__main__":
    main()
