import json
import unittest
from datetime import datetime
from pathlib import Path

from bro import Circle
from bro import Envelope
from bro import Point
from bro import RDPoint
from bro import get_cpt_characteristics
from bro import get_cpt_characteristics_and_return_cpt_objects
from bro import get_cpt_object


class TestPoint(unittest.TestCase):
    def setUp(self):
        self.wgs = Point(lat=51.998929, lon=4.375587)
        self.rd = RDPoint(x=85530.20712412785, y=446100.1761217844)

    def test_from_wgs84_to_rd_returns_correct_result(self):
        rd = self.wgs.from_wgs84_to_rd()

        expected_rd = self.rd
        self.assertAlmostEqual(rd.x, expected_rd.x)
        self.assertAlmostEqual(rd.y, expected_rd.y)

    def test_from_rd_to_wgs84_returns_correct_result(self):
        wgs = self.rd.from_rd_to_wgs84()
        expected_wgs = self.wgs

        self.assertAlmostEqual(wgs.lat, expected_wgs.lat)
        self.assertAlmostEqual(wgs.lon, expected_wgs.lon)


class TestCircle(unittest.TestCase):
    def setUp(self):
        self.circle = Circle(Point(lat=52.038297852, lon=5.31447958948), radius=0.5)

    def test_bro_json_property_has_correct_format(self):
        bro_json_actual = self.circle.bro_json

        bro_json_expected = {
            "enclosingCircle": {
                "center": {"lat": 52.038297852, "lon": 5.31447958948},
                "radius": 0.5,
            }
        }

        self.assertEqual(bro_json_actual, bro_json_expected)

    def test_to_geojson_feature_returns_correct_format(self):
        actual_geojson_feature = self.circle.to_geojson_feature

        expected_geojson_feature = {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [5.31447958948, 52.038297852]},
            "properties": {"description": f"Requested centroid"},
        }

        self.assertEqual(actual_geojson_feature, expected_geojson_feature)


class TestEnvelope(unittest.TestCase):
    def setUp(self):
        self.envelope = Envelope(
            lower_corner=Point(51.92269686635185, 4.469594207611851),
            upper_corner=Point(51.923034432171065, 4.470094707426648),
        )

    def test_bro_json_property_has_correct_format(self):
        bro_json_actual = self.envelope.bro_json

        bro_json_expected = {
            "boundingBox": {
                "lowerCorner": {
                    "lat": 51.92269686635185,
                    "lon": 4.469594207611851,
                },
                "upperCorner": {
                    "lat": 51.923034432171065,
                    "lon": 4.470094707426648,
                },
            }
        }

        self.assertEqual(bro_json_actual, bro_json_expected)

    def test_to_geojson_feature_returns_correct_format(self):
        actual_geojson_feature = self.envelope.to_geojson_feature

        expected_geojson_feature = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [4.469594207611851, 51.92269686635185],
                        [4.470094707426648, 51.92269686635185],
                        [4.470094707426648, 51.923034432171065],
                        [4.469594207611851, 51.923034432171065],
                        [4.469594207611851, 51.92269686635185],
                    ]
                ],
            },
            "properties": {"description": f"Requested area"},
        }

        self.assertEqual(actual_geojson_feature, expected_geojson_feature)


class TestAPI(unittest.TestCase):
    def test_get_cpt_object(self):
        bro_cpt_id = "CPT000000053405"
        response = get_cpt_object(bro_cpt_id, as_dict=True)

        with open(Path(__file__).parent / "response_CPT000000053405.json", "r") as f:
            expected_response = json.load(f)

        self.assertEqual(
            json.dumps(response["dispatchDocument"]),
            json.dumps(expected_response["dispatchDocument"]),
        )

    def test_get_cpt_characteristics_returns_correct_amount_of_results(self):
        # If the BRO gets updated the amount of available cpts in this area may change. As of 17/03/2023 this is valid.

        # Arrange
        begin_date = datetime(2015, 1, 1).strftime("%Y-%m-%d")
        end_date = datetime(2023, 3, 3).strftime("%Y-%m-%d")

        lower_corner = Point(51.92269686635185, 4.469594207611851)
        upper_corner = Point(51.923034432171065, 4.470094707426648)
        envelope = Envelope(lower_corner, upper_corner)

        # Act
        response = get_cpt_characteristics(begin_date, end_date, area=envelope)
        amount_of_available_cpts = 5

        # Assert
        self.assertEqual(len(response), amount_of_available_cpts)

    def test_get_cpt_characteristics_and_return_cpt_objects_returns_correct_result_type(
        self,
    ):
        # Arrange
        begin_date = datetime(2015, 1, 1).strftime("%Y-%m-%d")
        end_date = datetime(2023, 3, 3).strftime("%Y-%m-%d")

        lower_corner = Point(51.92269686635185, 4.469594207611851)
        upper_corner = Point(51.923034432171065, 4.470094707426648)
        envelope = Envelope(lower_corner, upper_corner)

        # Act
        response = get_cpt_characteristics_and_return_cpt_objects(begin_date, end_date, area=envelope, as_dict=True)

        # Assert
        self.assertIsInstance(response[0], dict)
