from io import BytesIO
from dataclasses import dataclass, field
from astropy.io.votable.tree import Table  # type: ignore
from astropy.io.votable import parse  # type: ignore
from tapvalidator.models.status import Status
from tapvalidator.logger.logger import logger
from tapvalidator.utility.xml_parser import XMLParser

__all__ = ["Result", "VOTable", "ValidationResult", "TableValidationResult"]


@dataclass
class Result:
    """Result class, represents the Result of a Query

    Attributes:
        data (str): The data represented as a string (default "")
        status (Status): The Status of the Result (default Status.Pending)
        messages (list): List of messages that need to be stored along with this Result
    """

    data: str = ""
    status: Status = Status.PENDING
    messages: list = field(default_factory=list)


@dataclass
class VOTable(Result):
    """Implementation of a Result, specifically a VOTable Result"""

    astropy_table: Table | None = None

    def parse_votable(self, data: str) -> Table | None:
        """Parse a VOTable
        Args:
            data (str): VOTable as string
        Returns:
            Table | None: The parsed table or None if there was an issue
        """
        astropy_table = None

        if not data:
            return None
        try:
            parsed_table = parse(BytesIO(bytes(self.data, "utf-8")))
            astropy_table = parsed_table.get_first_table()
        except Exception as exc:
            logger.error(exc)
            logger.error(
                f"Unable to parse Table from VOTable, "
                f"got following response: {self.data}"
            )
            self.status = Status.FAIL
            self.astropy_table = None

        if self.status is Status.FAIL:
            try:
                votable_error = XMLParser.get_votable_error(self.data)
            except Exception as exc:
                logger.error(exc)
                logger.error("Unable to parse Error from VOTable")
                votable_error = "Unknown error occured while trying to parse VOTable"
            self.messages.append(votable_error)
        return astropy_table

    def __post_init__(self):
        self.status = Status.SUCCESS
        self.astropy_table = self.parse_votable(self.data)

    def __eq__(self, other):
        if not isinstance(other, VOTable):
            return NotImplemented
        return self.data == other.data


@dataclass
class ValidationResult(Result):
    """Class representing the Result of a Validation
    Attributes:
        status (Status): The Status of the Result
        failures (list): The list of failed queries

    """

    failures: list = field(default_factory=list)
    status: Status = Status.PENDING

    def as_string(self, validation_type_str: str = "") -> str:
        """Get Validation Result as a string"""
        res = (
            f"{validation_type_str + ' ' if validation_type_str else ''}Validation "
            f"result: [{self.status}]\n"
        )
        if self.messages:
            res += "Relevant logs:\n"
            for message in self.messages:
                res += f"{message}\n"
        return res

    def __hash__(self):
        # Hash based on the tuple of attributes
        return hash((tuple(self.failures), self.status))

    def __eq__(self, other):
        if isinstance(other, ValidationResult):
            return (self.failures, self.status) == (other.failures, other.status)
        return False


@dataclass
class TableValidationResult(ValidationResult):
    """Class representing the Result of a Table Validation
    Attributes:
        status (Status): The Status of the Result
        failures (list): The list of failed queries
    """

    def as_string(self, validation_type_str: str = "Table") -> str:
        """Get Table Validation Result as a string"""
        res = (
            f"{validation_type_str + ' ' if validation_type_str else ''}"
            f"Validation result status: [{self.status}]\n"
        )
        if self.status is not Status.SUCCESS:
            res += "The following queries failed:\n"
            for query in self.failures:
                res += f"[{query.query_text}]\n"
                res += "Relevant logs:\n"
                for message in query.result.messages:
                    res += f"{message}\n"
        return res


@dataclass
class VOSIValidationResult(ValidationResult):
    """Class representing the Result of a VOSI Validation
    Attributes:
        status (Status): The Status of the Result
        failures (list): The list of failed queries
    """

    def as_string(self, validation_type_str: str = "VOSI") -> str:
        """Get VOSI Validation Result as a string"""
        res = (
            f"{validation_type_str + ' ' if validation_type_str else ''}"
            f"Validation result status: [{self.status}] \n"
        )
        if self.status is not Status.SUCCESS:
            res += "Relevant logs: \n"
            for message in self.messages:
                res += f"[{message}] \n"
        return res
