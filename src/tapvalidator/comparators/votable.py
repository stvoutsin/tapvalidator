from tapvalidator.models.result import VOTable


class VOTableComparator:
    """Comparator implementation for comparing two VOTables"""

    @staticmethod
    def compare(votable1: VOTable, votable2: VOTable) -> bool:
        """
        Compares two VOTable results to ensure they have the same number of rows.

        Args:
            votable1 (VOTable): The first VOTable result.
            votable2 (VOTable): The second VOTable result.

        Returns:
            bool: True if the VOTables have the same number of rows; False otherwise.
        """
        if len(votable1.data) == 0 and len(votable2.data) == 0:
            return True

        try:
            first_table1 = votable1.astropy_table
        except IndexError:
            first_table1 = None

        try:
            first_table2 = votable2.astropy_table
        except IndexError:
            first_table2 = None

        if not first_table2 and not first_table1:
            return True
        if not first_table2 or not first_table1:
            return False

        rows_length1 = first_table1.nrows
        rows_length2 = first_table2.nrows
        if rows_length1 != rows_length2:
            return False

        data1 = first_table1.array
        data2 = first_table2.array

        for i in range(len(data1)):
            for j in range(len(data1[i])):
                if data1[i][j] != data2[i][j]:
                    return False

        fields1 = first_table1.fields
        fields2 = first_table2.fields

        for i in range(len(fields1)):
            if (
                not fields1[i].ID == fields2[i].ID
                or not fields1[i].datatype == fields2[i].datatype
            ):
                return False
        return True
