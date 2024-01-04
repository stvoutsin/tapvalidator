"""
Dramatiq Tasks and Configuration
"""
import os
import time
import requests
from requests import HTTPError
import dramatiq  # type: ignore
from dramatiq.brokers.rabbitmq import RabbitmqBroker  # type: ignore
from dramatiq.brokers.stub import StubBroker  # type: ignore
from dramatiq.results.backends import RedisBackend  # type: ignore
from dramatiq.results import Results  # type: ignore
from tapvalidator.constants.tap_params import STANDARD_PARAMS
from tapvalidator.settings import settings
from tapvalidator.logger.logger import logger

result_backend = RedisBackend()
if os.getenv("UNIT_TESTS") == "1":
    broker = StubBroker()
    broker.emit_after("process_boot")
else:
    broker = RabbitmqBroker()

broker.add_middleware(Results(backend=result_backend))
dramatiq.set_broker(broker)


@dramatiq.actor(store_results=True)
def run_sync_query_task(query_text: str, tap_service_url: str) -> str:
    """Run a synchronous query

    Args:
        query_text (str): The query to be run
        tap_service_url (str): The URL of the TAP Service

    Returns:
        str: the result of the synchronous Query, as a string

    """
    params = {
        **STANDARD_PARAMS,
        "QUERY": query_text,
    }
    try:
        response = requests.get(
            tap_service_url,
            params=params,
            timeout=settings.http_timeout,
        )
    except HTTPError as http_error:
        logger.error(str(http_error))
        return str(http_error)
    time.sleep(1)

    logger.info(str(response.text))

    return response.text
