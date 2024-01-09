"""The Logger instance we are using for this module
Uses the structlog library
"""
import structlog
import functools

__all__ = ["logger", "query_validation_logger"]

logger = structlog.get_logger()


def query_validation_logger(func):
    from tapvalidator.models.query import Query

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            query = kwargs["query"] if "query" in kwargs else args[0]
            query = query if isinstance(query, Query) else None
        except IndexError:
            query = None

        if query:
            logger.info(
                f"Validating table [{query.table_name}]",
                table=query.table_name,
                query=query.query_text,
            )
            result = await func(*args, **kwargs)
            logger.info(
                f"Validation completed [{query.table_name}] [{ query.status}]",
                table=query.table_name,
            )
        else:
            result = func(*args, **kwargs)

        return result

    return wrapper
