import requests
from astropy.io.votable import parse
import io
from astropy.io.votable.tree import VOTableFile
import json
from typing import Protocol
import xml.etree.ElementTree as ET
import random
from time import sleep

STANDARD_PARAMS = {
    "LANG": "ADQL",
    "FORMAT": "VOTABLE",
    "REQUEST": "doQuery",
}

TAP_METADATA = {
    "http://tap.roe.ac.uk/osa": "https://raw.githubusercontent.com/wfau/metadata/master/firethorn"
    "/config/osa-tap.json",
    "http://tap.roe.ac.uk/vsa": "https://raw.githubusercontent.com/wfau/metadata/master/firethorn"
    "/config/vsa-tap.json",
    "http://tap.roe.ac.uk/wsa": "https://raw.githubusercontent.com/wfau/metadata/master/firethorn"
    "/config/wsa-tap.json",
    "http://tap.roe.ac.uk/ssa": "https://raw.githubusercontent.com/wfau/metadata/master/firethorn"
    "/config/ssa-tap.json",
}

RESERVED_KEYWORDS = {
    "FIRST",
    "DIAGNOSTICS",
    "REGION",
    "COLUMNS",
    "ABS",
    "ACOS",
    "ASIN",
    "ATAN",
    "ATAN2",
    "CEILING",
    "COS",
    "DEGREES",
    "EXP",
    "FLOOR",
    "LOG",
    "LOG10",
    "MOD",
    "PI",
    "POWER",
    "RADIANS",
    "RAND",
    "ROUND",
    "SIN",
    "SQRT",
    "TAN",
    "TOP",
    "TRUNCATE",
    "AREA",
    "BOX",
    "CENTROID",
    "CIRCLE",
    "CONTAINS",
    "COORD1",
    "COORD2",
    "COORDSYS",
    "DISTANCE",
    "INTERSECTS",
    "POINT",
    "POLYGON",
    "REGION",
    "ABSOLUTE",
    "ACTION",
    "ADD",
    "ALL",
    "ALLOCATE",
    "ALTER",
    "AND",
    "ANY",
    "ARE",
    "AS",
    "ASC",
    "ASSERTION",
    "AT",
    "AUTHORIZATION",
    "AVG",
    "BEGIN",
    "BETWEEN",
    "BIT",
    "BIT_LENGTH",
    "BOTH",
    "BY",
    "CASCADE",
    "CASCADED",
    "CASE",
    "CAST",
    "CATALOG",
    "CHAR",
    "CHARACTER",
    "CHARACTER_LENGTH",
    "CHAR_LENGTH",
    "CHECK",
    "CLOSE",
    "COALESCE",
    "COLLATE",
    "COLLATION",
    "COLUMN",
    "COMMIT",
    "CONNECT",
    "CONNECTION",
    "CONSTRAINT",
    "CONSTRAINTS",
    "CONTINUE",
    "CONVERT",
    "CORRESPONDING",
    "COUNT",
    "CREATE",
    "CROSS",
    "CURRENT",
    "CURRENT_DATE",
    "CURRENT_TIME",
    "CURRENT_TIMESTAMP",
    "CURRENT_USER",
    "CURSOR",
    "DATE",
    "DAY",
    "DEALLOCATE",
    "DECIMAL",
    "DECLARE",
    "DEFAULT",
    "DEFERRABLE",
    "DEFERRED",
    "DELETE",
    "DESC",
    "DESCRIBE",
    "DESCRIPTOR",
    "DIAGNOSTICS",
    "DISCONNECT",
    "DISTINCT",
    "DOMAIN",
    "DOUBLE",
    "DROP",
    "ELSE",
    "END",
    "END - EXEC",
    "ESCAPE",
    "EXCEPT",
    "EXCEPTION",
    "EXEC",
    "EXECUTE",
    "EXISTS",
    "EXTERNAL",
    "EXTRACT",
    "FALSE",
    "FETCH",
    "FIRST",
    "FLOAT",
    "FOR",
    "FOREIGN",
    "FOUND",
    "FROM",
    "FULL",
    "GET",
    "GLOBAL",
    "GO",
    "GOTO",
    "GRANT",
    "GROUP",
    "HAVING",
    "HOUR",
    "IDENTITY",
    "IMMEDIATE",
    "IN",
    "INDICATOR",
    "INITIALLY",
    "INNER",
    "INPUT",
    "INSENSITIVE",
    "INSERT",
    "INT",
    "INTEGER",
    "INTERSECT",
    "INTERVAL",
    "INTO",
    "IS",
    "ISOLATION",
    "JOIN",
    "KEY",
    "LANGUAGE",
    "LAST",
    "LEADING",
    "LEFT",
    "LEVEL",
    "LIKE",
    "LOCAL",
    "LOWER",
    "MATCH",
    "MAX",
    "MIN",
    "MINUTE",
    "MODULE",
    "MONTH",
    "NAMES",
    "NATIONAL",
    "NATURAL",
    "NCHAR",
    "NEXT",
    "NO",
    "NOT",
    "NULL",
    "NULLIF",
    "NUMERIC",
    "OCTET_LENGTH",
    "OF",
    "ON",
    "ONLY",
    "OPEN",
    "OPTION",
    "OR",
    "ORDER",
    "OUTER",
    "OUTPUT",
    "OVERLAPS",
    "PAD",
    "PARTIAL",
    "POSITION",
    "PRECISION",
    "PREPARE",
    "PRESERVE",
    "PRIMARY",
    "PRIOR",
    "PRIVILEGES",
    "PROCEDURE",
    "PUBLIC",
    "READ",
    "REAL",
    "REFERENCES",
    "RELATIVE",
    "RESTRICT",
    "REVOKE",
    "RIGHT",
    "ROLLBACK",
    "ROWS",
    "SCHEMA",
    "SCROLL",
    "SECOND",
    "SECTION",
    "SELECT",
    "SESSION",
    "SESSION_USER",
    "SET",
    "SIZE",
    "SMALLINT",
    "SOME",
    "SPACE",
    "SQL",
    "SQLCODE",
    "SQLERROR",
    "SQLSTATE",
    "SUBSTRING",
    "SUM",
    "SYSTEM_USER",
    "TABLE",
    "TEMPORARY",
    "THEN",
    "TIME",
    "TIMESTAMP",
    "TIMEZONE_HOUR",
    "TIMEZONE_MINUTE",
    "TO",
    "TRAILING",
    "TRANSACTION",
    "TRANSLATE",
    "TRANSLATION",
    "TRIM",
    "TRUE",
    "UNION",
    "UNIQUE",
    "UNKNOWN",
    "UPDATE",
    "UPPER",
    "USAGE",
    "USER",
    "USING",
    "VALUE",
    "VALUES",
    "VARCHAR",
    "VARYING",
    "VIEW",
    "WHEN",
    "WHENEVER",
    "WHERE",
    "WITH",
    "WORK",
    "WRITE",
    "YEAR",
    "ZONE",
}


class Alerter(Protocol):
    @staticmethod
    def send_alert():
        ...


class SlackAlerter:
    @staticmethod
    def send_alert(msg: str, destination: str):
        """
        Send a message to a Slack Channel, given a destination url
        """
        headers = {"content-type": "application/json"}
        r = requests.post(
            destination,
            headers=headers,
            json=json.dumps({"text": msg}),
            data=json.dumps({"text": msg}),
        )

        return r.text


AlertingStrategies = {"slack": SlackAlerter}


class TAPValidator:
    """
    A class for comparing results of SQL queries executed on two IVOA TAP services.

    Args:
        first_service (str): The URL of the first IVOA TAP service.
        service2_url (str): The URL of the second IVOA TAP service.
    """

    def __init__(
        self,
        first_service: str,
        second_service: str,
        alerting_strategy: Alerter = None,
        alert_destination: str = None,
    ):
        self.first_service = first_service
        self.second_service = second_service
        self.alerting_strategy = alerting_strategy
        self.alert_destination = alert_destination

    def run_query(self, query: str, url: str) -> tuple:
        """
        Run a synchronous Query
        Args:
            query (str): The query
            url (str): The URL
        Returns:
            tuple: The result status and message from the query
        """
        res = True
        msg = ""

        try:
            votable = self.fetch_votable(query, url)
            if votable:
                votable.get_first_table()
        except Exception:
            res = False
            msg = f"Problem encountered with TAP service: {url} \n Query: {query}"
        return res, msg

    def validate_service(self, url: str, full: bool = False):
        """
        Validate the service with a list of queries
        Args:
            url (str): TAP url
            full (bool): Whether to do a full scan
        """
        queries = self.generate_sql_queries(TAP_METADATA[url], full)
        for q in queries:
            sleep(3)
            res, msg = self.run_query(q, url)
            if self.alerting_strategy:
                if not res:
                    print(f"QUERY Failed: {q}")
                    self.send_alert(msg, self.alert_destination)

    def send_alert(self, msg: str, destination: str):
        """
        Send an alert to the destination
        Arg:
            msg (str): The message
            destination (str): The destination

        """
        self.alerting_strategy.send_alert(msg, destination)

    def fetch_votable(self, query: str, service_url: str) -> parse:
        """
        Fetches a VOTable result for a given SQL query from an IVOA TAP service.

        Args:
            query (str): The SQL query to be executed.
            service_url (str): The URL of the IVOA TAP service.

        Returns:
            parse_single_table: The parsed VOTable result.
        """
        params = {
            **STANDARD_PARAMS,
            "QUERY": query,
        }
        try:
            response = requests.get(service_url + "/sync", params=params, timeout=30)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            return parse(io.BytesIO(response.content))

        except requests.exceptions.Timeout:
            # Handle timeout, return an empty string in this case
            print("Request timed out")
            return ""

        return parse(io.BytesIO(response.content))

    def compare_votables(self, votable1: VOTableFile, votable2: VOTableFile) -> bool:
        """
        Compares two VOTable results to ensure they have the same number of rows.

        Args:
            votable1 (parse_single_table): The first VOTable result.
            votable2 (parse_single_table): The second VOTable result.

        Returns:
            bool: True if the VOTables have the same number of rows; False otherwise.
        """
        if len(votable1.resources) == 0 and len(votable2.resources) == 0:
            return True

        try:
            first_table1 = votable1.get_first_table()
        except IndexError:
            first_table1 = None

        try:
            first_table2 = votable2.get_first_table()
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

    def run_comparison(self, queries_file: str):
        """
        Runs the comparison for SQL queries stored in a text file.

        Args:
            queries_file (str): The path to the text file containing SQL queries.
        """
        with open(queries_file, "r") as file:
            queries = file.readlines()

        for query in queries:
            votable1 = self.fetch_votable(query, self.first_service)
            votable2 = self.fetch_votable(query, self.second_service)

            if self.compare_votables(votable1, votable2):
                print(f"{query} [OK]")
            else:
                print(f"{query} [FAIL]")

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

    def generate_sql_queries(self, json_url: str, full: bool) -> list:
        """
        Generate a list of SQL queries, given a WFAU TAP json configuration file
        Args:
            json_url (str): The JSON file (as string link)
            full (bool): Whether to generate a full list of all tables
        Returns:
            list: Query list
        """

        # Define the namespace
        def print_xml_structure(xml_content):
            root = ET.fromstring(xml_content)
            for elem in root.iter():
                print(elem.tag)

        # Fetch XML content from the URL
        response = requests.get(json_url)
        if response.status_code != 200:
            print(
                f"Failed to fetch JSON from {json_url}. Status code: {response.status_code}"
            )
            return
        content = response.json()
        queries = []
        for adql_resource in content["AdqlResources"]:
            for schema in adql_resource["Schemas"]:
                metadata_url = schema["metadata"]["metadoc"]

                # Read the XML content from the metadata URL
                metadata_response = requests.get(metadata_url)
                if metadata_response.status_code == 200:
                    metadata_xml = ET.fromstring(metadata_response.text)

                    # Find the Catalog element
                    catalog_element = metadata_xml.find(
                        ".//{urn:astrogrid:schema:TableMetaDoc:v1.1}Catalog"
                    )

                    if catalog_element is not None:
                        # Find all Table elements within Catalog
                        table_elements = catalog_element.findall(
                            ".//{urn:astrogrid:schema:TableMetaDoc:v1.1}Table"
                        )
                        if table_elements:
                            if not full:
                                table_elements = [random.choice(table_elements)]

                            for table_element in table_elements:
                                # Randomly select a table
                                # random_table_element = random.choice(table_elements)

                                # Get the name of the randomly selected table
                                table_name = table_element.find(
                                    ".//{urn:astrogrid:schema:TableMetaDoc:v1.1}Name"
                                ).text

                                schema_name = self.fix_keywords(schema["jdbccatalog"])
                                table_name = self.fix_keywords(table_name)
                                sql_query = (
                                    f"SELECT TOP 1 * FROM {schema_name}.{table_name}"
                                )
                                # Append the query to the list
                                queries.append(sql_query)
                        else:
                            print(
                                f"No Table elements found in the metadata XML for {metadata_url}"
                            )
                    else:
                        print(
                            f"No Catalog element found in the metadata XML for {metadata_url}"
                        )
                else:
                    print(f"Failed to fetch metadata from {metadata_url}")

        return queries


if __name__ == "__main__":
    service1_url = "http://tap.roe.ac.uk/osa"
    service2_url = "http://tap.roe.ac.uk/osa"
    queries_file = "data/queries.txt"
    slack_webhook = ""

    tap_validator = TAPValidator(
        first_service=service1_url,
        second_service=service2_url,
        alerting_strategy=AlertingStrategies["slack"],
        alert_destination=slack_webhook,
    )
    # tap_validator.run_comparison(queries_file)
    print("--- Validating OSA ----")
    tap_validator.validate_service("http://tap.roe.ac.uk/osa")
    print("--- Validating SSA ----")
    tap_validator.validate_service("http://tap.roe.ac.uk/ssa")
    print("--- Validating VSA ----")
    tap_validator.validate_service("http://tap.roe.ac.uk/vsa")
    print("--- Validating WSA ----")
    tap_validator.validate_service("http://tap.roe.ac.uk/wsa")
