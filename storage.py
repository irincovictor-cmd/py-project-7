"""
Storage module for School Parking and Vehicle Registration System.
Handles loading/saving of vehicle registry and entry/exit logs using JSON.
"""

import json
import os
from datetime import datetime, date
from copy import deepcopy

DATA_FILE = "parking_data.json"


def get_base_dir():
    return os.path.dirname(os.path.abspath(__file__))


def get_data_path():
    return os.path.join(get_base_dir(), DATA_FILE)


def default_data():
    """Fresh data with a few starter vehicles."""
    return {
        "vehicles": [
            {
                "vehicle_id": "V001",
                "plate_number": "ABC-1234",
                "owner_name": "Juan Dela Cruz",
                "owner_type": "Teacher",
                "vehicle_type": "Car",
                "color": "White",
                "notes": "Faculty parking"
            },
            {
                "vehicle_id": "V002",
                "plate_number": "XYZ-5678",
                "owner_name": "Maria Santos",
                "owner_type": "Staff",
                "vehicle_type": "Motorcycle",
                "color": "Black",
                "notes": ""
            },
            {
                "vehicle_id": "V003",
                "plate_number": "DEF-9012",
                "owner_name": "Visitor - Pedro Reyes",
                "owner_type": "Visitor",
                "vehicle_type": "Car",
                "color": "Silver",
                "notes": "Temporary visitor"
            },
            {
                "vehicle_id": "V004",
                "plate_number": "GHI-3456",
                "owner_name": "Ana Lim",
                "owner_type": "Teacher",
                "vehicle_type": "SUV",
                "color": "Blue",
                "notes": ""
            },
        ],
        "logs": [],
        "next_vehicle_id": 5,
        "next_log_id": 1
    }


def load_data():
    path = get_data_path()
    if not os.path.exists(path):
        data = default_data()
        save_data(data)
        return data
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for key in ["vehicles", "logs", "next_vehicle_id", "next_log_id"]:
            if key not in data:
                data[key] = default_data()[key]
        return data
    except (json.JSONDecodeError, OSError):
        data = default_data()
        save_data(data)
        return data


def save_data(data):
    path = get_data_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def generate_vehicle_id(data):
    vid = f"V{data['next_vehicle_id']:03d}"
    data["next_vehicle_id"] += 1
    return vid


def generate_log_id(data):
    lid = f"L{data['next_log_id']:03d}"
    data["next_log_id"] += 1
    return lid


def now_str():
    """Return current datetime as YYYY-MM-DD HH:MM"""
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def today_str():
    return date.today().isoformat()


def is_currently_parked(data, plate_number):
    """Return True if the vehicle has an open entry (no exit yet)."""
    for log in reversed(data["logs"]):
        if log["plate_number"].upper() == plate_number.upper():
            if log["status"] == "Inside":
                return True
            break
    return False


def get_open_log(data, plate_number):
    """Return the open log record for a plate, or None."""
    for log in reversed(data["logs"]):
        if log["plate_number"].upper() == plate_number.upper() and log["status"] == "Inside":
            return log
    return None
