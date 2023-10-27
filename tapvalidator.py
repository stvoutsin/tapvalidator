import requests
from astropy.io.votable import parse
import io
from astropy.io.votable.tree import VOTableFile
import json
from typing import Protocol

STANDARD_PARAMS = {
    "LANG": "ADQL",
    "FORMAT": "VOTABLE",
    "REQUEST": "doQuery",
}

VALIDATION_QUERIES = {
    "http://wfaudata.roe.ac.uk/osa": "SELECT TOP 10 * FROM ATLASDR1.Filter",
    "http://wfaudata.roe.ac.uk/vsa": "SELECT TOP 10 * FROM BestDR1.SpecObjAll",
    "http://wfaudata.roe.ac.uk/wsa": "SELECT TOP 10 * FROM BestDR1.SpecObjAll",
    "http://wfaudata.roe.ac.uk/ssa": "SELECT TOP 10 * FROM BestDR8.SpecObjAll",
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

    def validate_service(self, url: str):
        query = VALIDATION_QUERIES[url]
        res = True
        msg = ""

        try:
            votable = self.fetch_votable(query, url)
            votable.get_first_table()
        except Exception:
            res = False
            msg = f"Problem encountered with TAP service: {url} \n Query: {query}"
            if self.alerting_strategy:
                self.send_alert(msg, self.alert_destination)

        return (res, msg)

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
        response = requests.get(service_url + "/sync", params=params, timeout=100)
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


if __name__ == "__main__":
    service1_url = "http://wfaudata.roe.ac.uk/osa"
    service2_url = "http://tap.roe.ac.uk/osa"
    queries_file = "data/queries.txt"
    slack_webhook = "https://hooks.slack.com/services/.../"

    tap_validator = TAPValidator(
        first_service=service1_url,
        second_service=service2_url,
        alerting_strategy=AlertingStrategies["slack"],
        alert_destination=slack_webhook,
    )
    # query_comparer.run_comparison(queries_file)
    tap_validator.validate_service(service1_url)
