from dataclasses import dataclass
from typing import Optional, List

import shapely
from shapely.geometry.point import Point as SHPoint
from pyproj import Transformer


@dataclass
class Point:
    lat: float
    lon: float
    crs: Optional[str] = None

    @classmethod
    def from_wgs84_to_rd(cls, lat: float, lon: float) -> "Point":
        """Converts lat/Lon coordinates (EPSG: 4326) in degrees to RD coordinates (EPSG:28992)
        EPSG:4326 is WGS84
        EPSG:28992 is projected coordinate system Amersfoort / RD New in m

        :param lat: float latitude in degree (WGS84 / EPSG:4326)
        :param lon: float longitude in degree (WGS84 / EPSG4326)
        :return:
        """
        transformer = Transformer.from_crs(4326, 28992)
        rd_y, rd_x = transformer.transform(lat, lon)
        return cls(rd_y, rd_x)

    @classmethod
    def from_rd_to_wgs84(cls, x: float, y: float) -> "Point":
        """Converts RD coordinates (EPSG:28992) in m  to lat/Lon coordinates (EPSG: 4326) in degrees
        EPSG:4326 is WGS84
        EPSG:28992 is projected coordinate system Amersfoort / RD New in m

        :param x: float latitude in degree (RD New / EPSG:28992)
        :param y: float longitude in degree (RD New / EPSG:28992)
        :return:
        """
        transformer = Transformer.from_crs(28992, 4326)
        lat, lon = transformer.transform(x, y)
        return cls(lat, lon)


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
                    "bro_id": f""
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
                "prop": f"Requested area"
            }
        }
