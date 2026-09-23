import unittest
from unittest.mock import mock_open, patch

from utils import load_transactions


class TestLoadTransactions(unittest.TestCase):

    @patch("utils.open", mock_open(read_data='[{"id": 1, "amount": 100}]'))
    def test_load_valid_json(self):
        result = load_transactions("fake_path.json")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], 1)

    @patch("utils.open", side_effect=FileNotFoundError)
    def test_file_not_found(self, mock_open_func):
        result = load_transactions("nonexistent.json")
        self.assertEqual(result, [])

    @patch("utils.open", mock_open(read_data='"not a list"'))
    def test_invalid_json_structure(self):
        result = load_transactions("bad_format.json")
        self.assertEqual(result, [])
