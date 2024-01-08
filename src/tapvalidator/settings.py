import os
import configparser
import random
import string
from tapvalidator.constants.database_engines import str_to_db_engine

__all__ = ["Settings", "settings"]


class Settings:
    """Settings class, reads settings values from the settings.ini file into a
    Settings object"""

    def __init__(self):
        __filename__ = "settings.ini"
        config_path = os.path.join(os.path.dirname(__file__), __filename__)
        config = configparser.ConfigParser()
        config.read(config_path)
        self.database_engine = str_to_db_engine(config.get("Database", "engine"))
        self.query_delay = int(config.get("Time", "delay"))
        self.http_timeout = int(config.get("Time", "http_timeout"))
        self.max_parallel_tasks = int(config.get("Tasks", "max_parallel_tasks"))

        self.email_sender = config.get("Email", "sender", fallback=None)
        self.email_password = config.get("Email", "password", fallback=None)
        self.email_recipient = config.get("Email", "recipient", fallback=None)
        self.email_host = config.get("Email", "host", fallback=None)

        self.PYTHONASYNCIODEBUG = config.get("Env", "PYTHONASYNCIODEBUG")
        if self.PYTHONASYNCIODEBUG == "1":
            os.environ["PYTHONASYNCIODEBUG"] = self.PYTHONASYNCIODEBUG
        else:
            if "PYTHONASYNCIODEBUG" in os.environ:
                del os.environ["PYTHONASYNCIODEBUG"]
        self.redis_url = config.get("Redis", "url")

        self.id = "".join(
            random.choice(string.ascii_uppercase + string.digits) for _ in range(6)
        )


settings = Settings()
