from xml.etree import ElementTree

__all__ = ["XMLParser"]


class XMLParser:
    @staticmethod
    def get_votable_error(xml_string: str) -> str | None:
        """Get the error message from a failed query VOTable result
        Args:
            xml_string (str): The XML as a string

        Returns:
            str: The error message
        """
        root = ElementTree.fromstring(xml_string)
        namespace = {"votable": "http://www.ivoa.net/xml/VOTable/v1.3"}

        # Find the INFO element with the name "QUERY_STATUS"
        query_status_info = root.find(
            './/votable:INFO[@name="QUERY_STATUS"]', namespace
        )

        # Check if the INFO element exists
        if query_status_info is not None:
            return query_status_info.text
        else:
            return None

    @staticmethod
    def check_element_exists(xml_string: str, element: str) -> bool:
        """Check if a tables
        Args:
            xml_string (str): The XML as a string
            element (str): The element we are looking for
        Returns:
            bool: True if element found, False if not
        """
        root = ElementTree.fromstring(xml_string)
        if root.find(element) is not None:
            return True
        return False
