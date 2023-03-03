from pathlib import Path
from typing import Union

from lxml import etree

from .geometry import Point
from ..helpers.helper_functions import str2bool


class CPTCharacteristics:
    """
    Class to save all Characteristics of a CPT object, resulting from a characteristics search on the API
    """
    def __init__(self, parsed_dispatch_document: dict):
        self.gml_id: str = parsed_dispatch_document["gml:id"]
        self.bro_id: str = parsed_dispatch_document["brocom:broId"]
        self.deregistered: bool = str2bool(parsed_dispatch_document["brocom:deregistered"])
        self.accountable_party: int = parsed_dispatch_document["brocom:deliveryAccountableParty"]
        self.quality_regime: str = parsed_dispatch_document["brocom:qualityRegime"]
        self.object_registration_time: str = parsed_dispatch_document["brocom:objectRegistrationTime"]
        self.under_review: bool = str2bool(parsed_dispatch_document["brocom:underReview"])
        self.standardized_location: Point = Point(*tuple(elem for elem in parsed_dispatch_document["brocom:standardizedLocation"]["gml:pos"].split(' ')))  # to tuple or Point?
        self.delivered_location: Point = Point(*tuple(elem for elem in parsed_dispatch_document["brocom:deliveredLocation"]["gml:pos"].split(' ')))  # to tuple or Point?
        self.local_vertical_reference_point: str = parsed_dispatch_document["localVerticalReferencePoint"]["value"]
        self.vertical_datum: str = parsed_dispatch_document["verticalDatum"]["value"]
        self.cpt_standard: str = parsed_dispatch_document["cptStandard"]["value"]
        self.offset: float = float(parsed_dispatch_document["offset"]["value"])
        self.quality_class: str = parsed_dispatch_document["qualityClass"]
        self.research_report_date: str = parsed_dispatch_document["researchReportDate"]["brocom:date"]
        self.start_time: str = parsed_dispatch_document["startTime"]
        self.predrilled_depth: float = float(parsed_dispatch_document["predrilledDepth"]["value"]) if parsed_dispatch_document.get("predrilledDepth") else None
        self.final_depth: float = float(parsed_dispatch_document["finalDepth"]["value"])
        self.survey_purpose: str = parsed_dispatch_document["surveyPurpose"]["value"]
        self.dissipation_test_performed: bool = str2bool(parsed_dispatch_document["dissipationTestPerformed"])
        self.stop_criterion: str = parsed_dispatch_document["stopCriterion"]["value"]

    @property
    def to_geojson_feature(self) -> dict:
        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [self.wgs84_coordinates.lon, self.wgs84_coordinates.lat]
            },
            "properties": {
                "bro_id": f"{self.bro_id}"
            }
        }

    @property
    def rd_coordinates(self) -> Point:
        return self.delivered_location

    @property
    def wgs84_coordinates(self) -> Point:
        return self.standardized_location


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
                    (sub_child.tag.split("}")[-1], sub_child.text in {"ja", 1})
                    for sub_child in child
                ]
            else:
                grand_children[tag] = cls._parse_xml_to_dict_recursively(child)
        return grand_children
