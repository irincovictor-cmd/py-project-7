"""
Basic tests for the Parking system storage logic.
Run: python -m unittest discover -s tests -v
"""

import os
import sys
import unittest
import tempfile
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import storage


class TestStorage(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.original = storage.get_base_dir
        storage.get_base_dir = lambda: self.test_dir

    def tearDown(self):
        storage.get_base_dir = self.original
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_default_has_starter_vehicles(self):
        data = storage.default_data()
        self.assertGreaterEqual(len(data["vehicles"]), 3)
        self.assertEqual(data["logs"], [])

    def test_save_and_load(self):
        data = storage.default_data()
        storage.save_data(data)
        loaded = storage.load_data()
        self.assertEqual(len(loaded["vehicles"]), len(data["vehicles"]))

    def test_generate_ids(self):
        data = storage.default_data()
        vid = storage.generate_vehicle_id(data)
        self.assertTrue(vid.startswith("V"))
        lid = storage.generate_log_id(data)
        self.assertTrue(lid.startswith("L"))

    def test_is_currently_parked(self):
        data = storage.default_data()
        self.assertFalse(storage.is_currently_parked(data, "ABC-1234"))

        log = {
            "log_id": "L001",
            "plate_number": "ABC-1234",
            "owner_name": "Test",
            "time_in": storage.now_str(),
            "time_out": None,
            "status": "Inside"
        }
        data["logs"].append(log)
        self.assertTrue(storage.is_currently_parked(data, "ABC-1234"))
        self.assertFalse(storage.is_currently_parked(data, "ZZZ-9999"))


if __name__ == "__main__":
    unittest.main()
