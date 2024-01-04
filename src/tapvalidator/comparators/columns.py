from tapvalidator.models.result import VOTable
from tapvalidator.constants.vo_fields import convert_type
from tapvalidator.settings import settings
from tapvalidator.logger.logger import logger

__all__ = ["ColumnComparator"]


class ColumnComparator:
    """Class that contains methods to Compare the columns of a Return object (from a
    TAP Query) with the expected columns we get when checking the table in TAP_SCHEMA

    Methods:
        compare_columns (actual_columns: Result, expected_columns: Result) -> bool

    """

    @staticmethod
    def compare(actual: VOTable, expected: VOTable) -> bool:
        """
        Compare the columns we get from a query to a table in TAP, with the expected
        columns we see in TAP_SCHEMA for that table
        Args:
            actual (VOTable):The actual columns we got for the query
            expected (VOTable): The expected columns in TAP_SCHEMA

        Returns:
            bool: Whether the comparison was successful or not
        """

        def _get_columns_from_votable_fields(result: VOTable) -> dict:
            """Internal method used to extract a mapping of column name to datatype
            from the fields of a VOTable

            Args:
                result (Result): The result object
            Returns:
                dict: The mapping
            """
            mapping = {}
            for field in result.astropy_table.fields:
                mapping[field.ID] = field.datatype
            return mapping

        def _get_columns_from_votable_data(result: VOTable) -> dict:
            """Internal method used to extract a mapping of column name to
            datatype from the rows of a VOTable

            Args:
                result (Result): The result object
            Returns:
                dict: The mapping
            """

            mapping = {}
            for key, val in result.astropy_table.array:
                mapping[key] = val
            return mapping

        actual_columns = _get_columns_from_votable_fields(actual)
        expected_columns = _get_columns_from_votable_data(expected)

        for k, v in actual_columns.items():
            expected_col = convert_type(settings.database_engine, expected_columns[k])
            if expected_col == v:
                continue
            else:
                logger.error(
                    f"Expected "
                    f"{convert_type(settings.database_engine, expected_columns[k])} "
                    f" got {v} instead"
                )
                return False

        return True
