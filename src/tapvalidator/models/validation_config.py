"""Configuration definition."""
from dataclasses import dataclass, field
from tapvalidator.services.alerter import Alerter, AlertingStrategies, AlertStrategy
from tapvalidator.models.tap_service import TAPService

__all__ = [
    "ValidationConfiguration",
]


@dataclass
class ValidationConfiguration:
    """Data Class for storing the configuration of a validation run

    Attributes:
        first_service (str): The URL of the first TAP Service we are validating
        queries (str): A path to a queries file, if comparing two TAP Services,
        with a specified list
        alerter (Alerter): The Alerter that we are using for Notifications
        alert_destination (str): The Alert destination as a string (i.e. URL) (default:
        None)
        second_service (str): The second TAP Service URL, used if comparing two TAP
        services
    """

    first_service: TAPService
    queries: str | None = None
    alerter: Alerter = AlertingStrategies[AlertStrategy.LOG]
    alert_destination: str = ""
    second_service: TAPService = field(default_factory=TAPService)
