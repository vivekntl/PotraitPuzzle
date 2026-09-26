"""Verify that Pillow is installed and can load an image."""

from pathlib import Path
import unittest

from PIL import Image

FIXTURE = Path(__file__).parent / "fixtures" / "sample.png"


class PillowLoadTest(unittest.TestCase):
    def test_pillow_can_load_an_image(self) -> None:
        with Image.open(FIXTURE) as image:
            image.load()
            self.assertEqual(image.size, (8, 8))
            self.assertEqual(image.format, "PNG")


if __name__ == "__main__":
    unittest.main()
