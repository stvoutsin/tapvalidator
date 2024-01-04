from tapvalidator.constants.reserved_keywords import RESERVED_KEYWORDS
from tapvalidator.models.tap_service import TAPService
from tapvalidator.models.result import Result

__all__ = ["StringProcessor"]


class StringProcessor:
    @staticmethod
    def fix_keywords(string: str) -> str:
        """
        Add quotes around keywords in a query
        Args:
            string (str): The query

        Returns:
            str: The updated query
        """
        if string.upper() in RESERVED_KEYWORDS:
            return f'"{string}"'
        else:
            return string

    @staticmethod
    def generate_alert_message(
        string: str, tap_service: TAPService, result: Result
    ) -> str:
        """Generate the content of an alert message for a failed query
        Args:
            string (str): The query
            tap_service(str): The TAP Service
            result (Result): Result for failed query
        Returns:
            str: The updated query
        """
        res = f"Query: {string} to TAP Service: {tap_service} failed!\n"
        if result:
            res += "Relevant logs: \n"
            for message in result.messages:
                res += f"{message}\n"

        return res
