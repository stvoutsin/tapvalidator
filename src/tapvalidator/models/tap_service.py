from dataclasses import dataclass
import random
import string

__all__ = ["TAPEndpoints", "TAPService"]


@dataclass
class TAPEndpoints:
    """Dataclass which provides properties for getting
    the various endpoints of a TAP Service"""

    url: str

    @property
    def synchronous(self):
        return f"{self.url}/sync"

    @property
    def asynchronous(self):
        return f"{self.url}/async"

    @property
    def tables(self):
        return f"{self.url}/tables"

    @property
    def capabilities(self):
        return f"{self.url}/capabilities"

    @property
    def availability(self):
        return f"{self.url}/availability"


@dataclass
class TAPService:
    """TAP Service class, used for representing a TAP Service
    Attributes:
        url (str): The URL of the TAP Service
        name (str): A name for the TAP Service (Optional)
        endpoints (TAPEndpoints): The TAPEndpoints object for this TAP Service
    """

    url: str = ""
    name: str = ""
    endpoints: TAPEndpoints = None

    def __post_init__(self):
        self.endpoints = TAPEndpoints(self.url)
        if not isinstance(self.url, str):
            raise ValueError(f"Invalid URL provided: {self.url}")
        if not self.name:
            self.name = "".join(
                random.choice(
                    string.ascii_uppercase + string.ascii_lowercase + string.digits
                )
                for _ in range(16)
            )

    def __repr__(self):
        return self.url

    def __str__(self):
        return self.url
