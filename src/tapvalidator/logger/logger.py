"""The Logger instance we are using for this module
Uses the structlog library
"""
import structlog
import functools


__all__ = ["logger", "query_validation_logger"]

logger = structlog.get_logger()


def query_validation_logger(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        if len(args) == 3:
            logger.info(
                f"Validating table [{args[1].table_name}]",
                table=args[1].table_name,
                query=args[1].query_text,
            )
            result = await func(*args, **kwargs)
            logger.info(
                f"Validation completed [{args[1].table_name}] [{args[1].status}]",
                table=args[1].table_name,
            )
        else:
            result = func(*args, **kwargs)

        return result

    return wrapper
