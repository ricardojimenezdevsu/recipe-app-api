"""
Sample tests
"""
from django.test import SimpleTestCase

from app import calc

class CalcTests(SimpleTestCase):
    """Test the calc module."""

    def test_add_numbers(self):
        """Test adding number together."""
        res = calc.add(4, 3)

        self.assertEqual(res, 7)

    def test_subtract_numbers(self):
        """Test subtracting numbers."""
        res = calc.subtract(50, 10)

        self.assertEqual(res, 40)
