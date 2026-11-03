# School Parking and Vehicle Registration System

A simple offline desktop prototype for registering vehicles and logging daily entry/exit at a school campus.

Built with Python and Tkinter. Data is stored locally in JSON. No internet or external packages required.

## Features

- Register vehicles (plate number, owner, type, color)
- Search and manage registered vehicles
- Log vehicle ENTRY (time in)
- Log vehicle EXIT (time out)
- View currently parked vehicles
- Daily entry/exit logs
- Simple reports
- Data validation and duplicate plate prevention

## Requirements

- Python 3.10 or newer
- Tkinter (included with most Python installations on Windows)

## How to Run

```powershell
git clone https://github.com/irincovictor-cmd/py-project-7.git
cd py-project-7
python main.py
```

On first launch the system creates `parking_data.json` with a few sample vehicles.

## Project Structure

- `main.py` – GUI and application logic
- `storage.py` – JSON load/save and helper functions
- `tests/` – Automated tests
- `parking_data.json` – Created at runtime (not committed)

## Notes

This is a classroom prototype for a single computer. It is not a multi-user networked parking system.
