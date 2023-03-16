from dataclasses import dataclass
from pathlib import Path

from pyproj import Transformer
from typing import Union, List

import requests
import xmltodict

from .helper_functions import _str2bool
from .objects import IMBROFile

about = {}
with open(Path(__file__).parent / '__version__.py', 'r') as f:
    exec(f.read(), about)

REQUEST_REFERENCE = f"Requested-with-bro-v{about['__version__']}"
CPT_OBJECT_URL = "https://publiek.broservices.nl/sr/cpt/v1/objects/"
CPT_CHARACTERISTICS_URL = f"https://publiek.broservices.nl/sr/cpt/v1/characteristics/searches?requestReference={REQUEST_REFERENCE}"


@dataclass
class RDPoint:
    x: float
    y: float

    def from_rd_to_wgs84(self) -> "Point":
        """Converts RD coordinates (EPSG:28992) in m  to lat/lon coordinates (EPSG: 4326) in degrees
        EPSG:4326 is WGS84
        EPSG:28992 is projected coordinate system Amersfoort / RD New in m

        :param x: float latitude in degree (RD New / EPSG:28992)
        :param y: float longitude in degree (RD New / EPSG:28992)
        :return:
        """
        transformer = Transformer.from_crs(28992, 4326)
        lat, lon = transformer.transform(self.x, self.y)
        return Point(lat, lon)


@dataclass
class Point:
    lat: float
    lon: float

    def from_wgs84_to_rd(self) -> "RDPoint":
        """Converts lat/Lon coordinates (EPSG: 4326) in degrees to RD coordinates (EPSG:28992)
        EPSG:4326 is WGS84
        EPSG:28992 is projected coordinate system Amersfoort / RD New in m

        :param lat: float latitude in degree (WGS84 / EPSG:4326)
        :param lon: float longitude in degree (WGS84 / EPSG:4326)
        :return:
        """
        transformer = Transformer.from_crs(4326, 28992)
        rd_y, rd_x = transformer.transform(self.lat, self.lon)
        return RDPoint(rd_y, rd_x)


@dataclass
class Circle:
    center: Point
    radius: float
    """
    center: Point 
    radius: circle radius in km
    """

    @property
    def bro_json(self):
        return {
            "enclosingCircle": {
                "center": {
                    "lat": self.center.lat,
                    "lon": self.center.lon
                },
                "radius": self.radius
            }
        }

    @property
    def to_geojson_feature(self):
        return {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [self.center.lon, self.center.lat]
                },
                "properties": {
                    "description": f"Requested centroid"
                }
            }


@dataclass
class Envelope:
    lower_corner: Point
    upper_corner: Point

    @property
    def bro_json(self):
        return {
            "boundingBox": {
                "lowerCorner": {
                    "lat": self.lower_corner.lat,
                    "lon": self.lower_corner.lon,
                },
                "upperCorner": {
                    "lat": self.upper_corner.lat,
                    "lon": self.upper_corner.lon,
                },
            }
        }

    @property
    def to_geojson_feature(self) -> dict:
        return {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [self.lower_corner.lon, self.lower_corner.lat],
                    [self.upper_corner.lon, self.lower_corner.lat],
                    [self.upper_corner.lon, self.upper_corner.lat],
                    [self.lower_corner.lon, self.upper_corner.lat],
                    [self.lower_corner.lon, self.lower_corner.lat],
                ]
                ]
            },
            "properties": {
                "description": f"Requested area"
            }
        }


class CPTCharacteristics:
    """
    Class to save all Characteristics of a CPT object, resulting from a characteristics search on the API
    """
    def __init__(self, parsed_dispatch_document: dict):
        self.gml_id: str = parsed_dispatch_document["gml:id"]
        self.bro_id: str = parsed_dispatch_document["brocom:broId"]
        self.deregistered: bool = _str2bool(parsed_dispatch_document["brocom:deregistered"])
        self.accountable_party: int = parsed_dispatch_document["brocom:deliveryAccountableParty"]
        self.quality_regime: str = parsed_dispatch_document["brocom:qualityRegime"]
        self.object_registration_time: str = parsed_dispatch_document["brocom:objectRegistrationTime"]
        self.under_review: bool = _str2bool(parsed_dispatch_document["brocom:underReview"])
        self.standardized_location: Point = Point(*tuple(elem for elem in parsed_dispatch_document["brocom:standardizedLocation"]["gml:pos"].split(' ')))
        self.delivered_location: RDPoint = RDPoint(*tuple(elem for elem in parsed_dispatch_document["brocom:deliveredLocation"]["gml:pos"].split(' ')))
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
        self.dissipation_test_performed: bool = _str2bool(parsed_dispatch_document["dissipationTestPerformed"])
        self.stop_criterion: str = parsed_dispatch_document["stopCriterion"]["value"]

    @property
    def to_geojson_feature(self) -> dict:
        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [self.wgs84_coordinate.lon, self.wgs84_coordinate.lat]
            },
            "properties": {
                "bro_id": f"{self.bro_id}"
            }
        }

    @property
    def rd_coordinate(self) -> RDPoint:
        return self.delivered_location

    @property
    def wgs84_coordinate(self) -> Point:
        return self.standardized_location


def get_cpt_characteristics_and_return_cpt_objects(
    begin_date: str,
    end_date: str,
    area: Union[Circle, Envelope],
    as_dict: bool = False,
) -> List[Union[bytes, dict]]:
    """
    TODO: Add
    Note: It is not allowed to have more than 1000 objects in one request (or more than 500 MB), the request will fail otherwise.
    :param begin_date: date str in format YYYY-mm-dd (.strftime("%Y-%m-%d")) and should be > 2015-01-01
    :param end_date: date str in format YYYY-mm-dd (.strftime("%Y-%m-%d"))
    :param area: Union[Circle, Envelope] definition of area in which to look for CPT objects
    :param as_dict: bool indicating whether the returned objects should be xml_bytes (as_dict=False) or as dict (bool=True)
    :return: A list of xml bytes or a the parsed xml in dictionary format.
    """
    available_cpts = get_cpt_characteristics(begin_date, end_date, area)

    # TODO: Add logging for amount of cpts to be retrieved

    # Retrieve the objects in series
    bro_cpt_objects = []
    for available_cpt in available_cpts:
        cpt_obj = get_cpt_object(available_cpt.bro_id, as_dict=as_dict)
        bro_cpt_objects.append(cpt_obj)

    return bro_cpt_objects


def get_cpt_characteristics(
    begin_date: str,
    end_date: str,
    area: Union[Circle, Envelope]
) -> list:
    """ Retrieves available CPT Objects from the BRO in given date / area range.

    :param begin_date: str date in format YYYY-mm-dd (.strftime("%Y-%m-%d")) and should be > 2015-01-01
    :param end_date: str date in format YYYY-mm-dd (.strftime("%Y-%m-%d"))
    :param area: Union[Circle, Envelope] definition of area in which to look for CPT objects
    :return: A list of objects containing metadata of available CPT objects, WITHOUT actual measurements
    """

    headers = {
        "accept": "application/xml",
        "Content-Type": "application/json",
    }

    json = {
        "registrationPeriod": {
            "beginDate": begin_date,
            "endDate": end_date,
        },
        "area": area.bro_json
    }

    response = requests.post(
        CPT_CHARACTERISTICS_URL,
        headers=headers,
        json=json,
    )

    available_cpt_objects = []
    # Check status codes, if 200 return, if 400 get json with description
    if response.status_code == 200:
        parsed = xmltodict.parse(response.content, attr_prefix="", cdata_key="value")
        if parsed['dispatchCharacteristicsResponse']["numberOfDocuments"] == 0:
            raise ValueError("No available objects have been found in given date + area range. Retry with different parameters.")

        for document in parsed['dispatchCharacteristicsResponse']['dispatchDocument']:
            # TODO: Hard skip, this is likely to happen when it's deregistered. document will have key ["BRO_DO"]["brocom:deregistered"] = "ja"
            # TODO: Add this information to logger
            if "CPT_C" not in document.keys():
                continue
            available_cpt_objects.append(CPTCharacteristics(document["CPT_C"]))
        return available_cpt_objects
    response.raise_for_status()


def get_cpt_object(
    bro_cpt_id: str,
    as_dict: bool = False
) -> Union[bytes, dict]:
    """ Performs GET request on BRO API to retrieve a CPT object.

    :param bro_cpt_id: BRO CPT ID in str format, retrievable from CPTCharacteristics
    :param as_dict: bool indicating whether the returned xml in bytes format needs to be parsed to dict.
    :return: XML bytes CPT file directly from BRO REST API or dict of given XML file
    """
    headers = {
        "accept": "application/xml",
    }

    response = requests.get(
        f"{CPT_OBJECT_URL}{bro_cpt_id}?requestReference={REQUEST_REFERENCE}",
        headers=headers,
    )
    # Check status code, 200 -> xml, 400 -> json
    if response.status_code == 200:
        if as_dict:
            return IMBROFile(response.content).parse()
        return response.content
    response.raise_for_status()
