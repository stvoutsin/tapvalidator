from typing import Protocol, Type
import requests
from enum import Enum
import json
from tapvalidator.logger.logger import logger
from tapvalidator.settings import settings

__all__ = [
    "Alerter",
    "AlertStrategy",
    "SlackAlerter",
    "LogAlerter",
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

    SLACK = "SLACK"
    EMAIL = "EMAIL"
    LOG = "LOG"


class SlackAlerter:
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


class LogAlerter:
    """Alerting implementation for notifying a log"""

    @staticmethod
    def send_alert(msg: str, destination: str) -> str:
        """Send a message to a log"""
        logger.info(msg, destination=destination)
        return msg


class EmailAlerter:
    """Alerting implementation for notifying a log"""

    @staticmethod
    def send_alert(msg: str, destination: str) -> str:
        """Send a message to an email"""
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        sender_email = settings.email_sender
        sender_password = settings.email_password
        recipient_email = settings.email_recipient

        # Create message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = destination
        message["Subject"] = "TAP Validation Alert"
        body = msg
        message.attach(MIMEText(body, "plain"))

        # Establish a connection to the SMTP server (in this case, Gmail's SMTP server)
        with smtplib.SMTP(settings.email_host, 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())

        return msg


class AlerterResolver:
    """Alerting Strategies class
    Allows to get Alerter given an AlertStrategy as a string"""

    @staticmethod
    def get_alerter(
        alert_type: str,
    ) -> Type[SlackAlerter] | Type[LogAlerter] | Type[EmailAlerter]:
        """Get Alert Strategy, given an AlertStrategy Enum value

        Args:
            alert_type (str): The alert type as a string
        Returns:
            Alerter: The equivalent Alerter
        """
        match alert_type.upper():
            case AlertStrategy.SLACK.value:
                return SlackAlerter
            case AlertStrategy.EMAIL.value:
                return EmailAlerter
            case _:
                return LogAlerter


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
