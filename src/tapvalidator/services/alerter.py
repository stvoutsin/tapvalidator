from typing import Protocol, Type
import requests
from enum import Enum, auto
import json
from tapvalidator.logger.logger import logger

__all__ = [
    "Alerter",
    "AlertStrategy",
    "SlackAlerter",
    "LogAlerter",
    "AlerterFactory",
    "AlerterService",
    "AlerterResolver",
]


class Alerter(Protocol):
    """Alerter Protocol, defined the methods that are expected to be implemented by
    a class that
    allows alerting / notifying"""

    @staticmethod
    def send_alert(msg: str, destination: str) -> str:
        """Sends an alert"""
        ...


class AlertStrategy(Enum):
    """Enum defining the available Alerting Channels"""

    SLACK = auto()
    EMAIL = auto()
    LOG = auto()


class SlackAlerter(Alerter):
    """Slack Alerter, implementation of the Alert Protocol, sends an alert to a
    Slack channel"""

    @staticmethod
    def send_alert(msg: str, destination: str) -> str:
        """Send a message to a Slack Channel, given a destination url

        Args:
            msg (str): The message to send to the channel
            destination (str): The destination to which to send the msg to (URL String)

        Returns:
            str: The response of the sent HTTP request to the channel
        """
        headers = {"content-type": "application/json"}
        r = requests.post(
            destination,
            headers=headers,
            json=json.dumps({"text": msg}),
            data=json.dumps({"text": msg}),
        )

        return r.text


class LogAlerter(Alerter):
    """Alerting implementation for notifying a log"""

    @staticmethod
    def send_alert(msg: str, destination: str) -> str:
        """Send a message to a log"""
        logger.info(msg, destination=destination)
        return msg


"""Map of AlertStrategies, to their equivalent Alerters"""


class AlerterResolver:
    """Alerting Strategies class
    Allows to get Alerter given an AlertStrategy ENUM value"""

    ALERTER_MAP = {
        AlertStrategy.SLACK: SlackAlerter,
        AlertStrategy.LOG: LogAlerter,
    }

    @staticmethod
    def get_strategy(alert_strategy: AlertStrategy) -> Type[Alerter]:
        """Get Alert Strategy, given an AlertStrategy Enum value

        Args:
            alert_strategy:
        Returns:
            Alerter: The equivalent Alerter
        """
        return AlerterResolver.ALERTER_MAP[alert_strategy]


class AlerterService:
    @staticmethod
    def send_alert(msg: str, destination: str, alerter: Alerter):
        """Send an alert to the destination
        Arg:
            msg (str): The message
            destination (str): The destination
            alerter (Alerter): The Alerter to use
        """
        alerter.send_alert(msg, destination)


class AlerterFactory:
    @staticmethod
    def get_alerter(slack_webhook: str | None) -> Alerter:
        """Get the alerting strategy, given a Slack Webhook value passed in to the
        Validator

        Args:
            slack_webhook (str): An Slack webhook (Could be None)

        Returns:
            Alerter: The equivalent Alerter

        """

        if slack_webhook:
            return AlerterResolver.get_strategy(AlertStrategy.SLACK)
        else:
            return AlerterResolver.get_strategy(AlertStrategy.LOG)
