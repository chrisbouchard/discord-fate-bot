from unittest import TestCase

from discord_fate_bot.dice import Value

class DiceValueTests(TestCase):
    """Tests for dice.Value"""

    def test_add_two_values(self):
        """Test for Value + Value"""
        result = Value(1) + Value(2)
        self.assertEqual(result, Value(3))

    def test_add_value_int(self):
        """Test for Value + int"""
        result = Value(2) + 3
        self.assertEqual(result, Value(5))

    def test_add_int_value(self):
        """Test for int + Value"""
        result = 3 + Value(4)
        self.assertEqual(result, Value(7))

