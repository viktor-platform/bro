import unittest
from pathlib import Path

from bro import IMBROFile


class TestIMBROFile(unittest.TestCase):
    def test_from_file_returns_objects(self):
        # Arrange
        xml_file = Path(__file__).parent / "response_CPT000000053405.xml"

        # Act
        imbro_file = IMBROFile.from_file(xml_file)

        # Assert
        self.assertIsInstance(imbro_file, IMBROFile)
