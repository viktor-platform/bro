from pathlib import Path
from typing import Union

from lxml import etree


class IMBROFile:
    """
    Class to handle paring of BRO XML files, currently working for the CPT API.
    """

    def __init__(self, file_content: bytes):
        self.file_content = file_content

    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> "IMBROFile":
        """Instantiates the IMBROFile class from a file_path to an IMBRO xml file."""
        with Path(file_path).open("rb") as xml_file:
            file_content = xml_file.read()
        return cls(file_content=file_content)

    def parse(
        self,
    ) -> dict:
        """Parses the xml file and returns a dictionary object"""
        xml_dict = self._parse_xml_file(self.file_content)
        return xml_dict

    def _parse_xml_file(self, file_content: bytes) -> dict:
        return self._parse_xml_to_dict_recursively(etree.fromstring(file_content))

    @classmethod
    def _parse_xml_to_dict_recursively(cls, node) -> dict:
        """Builds the data object from the xml structure passed, therefore preserving the structure and the values."""
        if not node.getchildren():
            return node.text

        grand_children = {}
        for child in node.getchildren():
            tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
            if tag == "parameters":
                grand_children["parameters"] = [
                    (sub_child.tag.split("}")[-1], sub_child.text in {"ja", 1}) for sub_child in child
                ]
            else:
                grand_children[tag] = cls._parse_xml_to_dict_recursively(child)
        return grand_children
