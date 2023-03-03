from typing import Union, List

import requests
import xmltodict


from ..bro_objects.cpt import CPTCharacteristics
from ..bro_objects.cpt import IMBROFile
from ..bro_objects.geometry import Circle
from ..bro_objects.geometry import Envelope


CPT_OBJECT_URL = "https://publiek.broservices.nl/sr/cpt/v1/objects/"
CPT_CHARACTERISTICS_URL = "https://publiek.broservices.nl/sr/cpt/v1/characteristics/searches"


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
    available_cpts: List[CPTCharacteristics] = get_cpt_characteristics(begin_date, end_date, area)

    # TODO: Add logging for amount of cpts to be retrieved

    # Retrieve the objects in series
    bro_cpt_objects: List = []
    for available_cpt in available_cpts:
        cpt_obj = get_cpt_object(available_cpt.bro_id, as_dict=as_dict)
        bro_cpt_objects.append(cpt_obj)

    return bro_cpt_objects


def get_cpt_characteristics(
    begin_date: str,
    end_date: str,
    area: Union[Circle, Envelope]
) -> List[CPTCharacteristics]:
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
                print(document["brocom:BRO_DO"])
                continue
            cpt_obj = CPTCharacteristics(document["CPT_C"])
            available_cpt_objects.append(CPTCharacteristics(document["CPT_C"]))
            # print(cpt_obj.deregistered, cpt_obj.to_geojson_feature)
        print("available objects:", len(available_cpt_objects))
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
        f"{CPT_OBJECT_URL}{bro_cpt_id}",
        headers=headers,
    )
    # Check status code, 200 -> xml, 400 -> json
    if response.status_code == 200:
        if as_dict:
            return IMBROFile(response.content).parse()
        return response.content
    response.raise_for_status()
