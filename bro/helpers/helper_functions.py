import json
from typing import List

from ..bro_objects.geometry import Envelope


def str2bool(s) -> bool:
    """
    converts a value to bool based on certain
    :param s: int, str, float
    :return: bool
    """
    return str(s).lower() in ("ja", "yes", "true", "t", "1")


def construct_valid_geojson_from_characteristics(
        characteristics: List,
        area: Envelope = None,
) -> str:
    """Generates a str containing a valid geojson structure from separate objects.

    :param characteristics: List of CPTCharacteristics objects
    :param area: Envelope. Circle are not yet supported
    :return: str in geojson format that contains of requested area + available objects in that area
    """
    # TODO: Add Circle area as polygon, Circle with shapely?

    features = [characteristic.to_geojson_feature for characteristic in characteristics]
    if isinstance(area, Envelope):
        features += [area.to_geojson_feature]

    return json.dumps(
        {
            "type": "FeatureCollection",
            "features": features
        }
    )
