"""
School Parking and Vehicle Registration System
Simple offline prototype using Python + Tkinter.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

import storage


class ParkingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("School Parking and Vehicle Registration System")
        self.root.geometry("1050x650")
        self.root.minsize(950, 600)

        self.data = storage.load_data()
        self._build_ui()
        self.refresh_all()

    def _build_ui(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Top bar
        top = ttk.Frame(self.root, padding=8)
        top.pack(fill=tk.X)

        ttk.Label(
            top,
            text="School Parking & Vehicle Registration System",
            font=("Segoe UI", 16, "bold")
        ).pack(side=tk.LEFT)

        self.status_var = tk.StringVar()
        ttk.Label(top, textvariable=self.status_var, font=("Segoe UI", 10)).pack(side=tk.RIGHT)

        # Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        self.tab_vehicles = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(self.tab_vehicles, text="  Vehicle Registry  ")
        self._build_vehicles_tab()

        self.tab_entry = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(self.tab_entry, text="  Entry / Exit Log  ")
        self._build_entry_tab()

        self.tab_reports = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(self.tab_reports, text="  Reports  ")
        self._build_reports_tab()

    # ------------------------------------------------------------------
    # Vehicle Registry Tab
    # ------------------------------------------------------------------
    def _build_vehicles_tab(self):
        search_frame = ttk.Frame(self.tab_vehicles)
        search_frame.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(search_frame, text="Search (Plate / Owner):").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh_vehicles())
        ttk.Entry(search_frame, textvariable=self.search_var, width=35).pack(side=tk.LEFT, padx=6)
        ttk.Button(search_frame, text="Refresh", command=self.refresh_all).pack(side=tk.RIGHT)

        content = ttk.Frame(self.tab_vehicles)
        content.pack(fill=tk.BOTH, expand=True)

        # Left: list
        left = ttk.Frame(content)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        columns = ("vehicle_id", "plate", "owner", "owner_type", "vehicle_type", "color")
        self.tree_vehicles = ttk.Treeview(left, columns=columns, show="headings", height=18)
        headings = ["ID", "Plate Number", "Owner Name", "Owner Type", "Vehicle Type", "Color"]
        widths = [60, 110, 160, 100, 110, 80]
        for col, text, w in zip(columns, headings, widths):
            self.tree_vehicles.heading(col, text=text)
            self.tree_vehicles.column(col, width=w, anchor=tk.CENTER if col != "owner" else tk.W)

        scrollbar = ttk.Scrollbar(left, orient=tk.VERTICAL, command=self.tree_vehicles.yview)
        self.tree_vehicles.configure(yscrollcommand=scrollbar.set)
        self.tree_vehicles.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_vehicles.bind("<<TreeviewSelect>>", self.on_vehicle_select)

        # Right: form
        right = ttk.Frame(content, padding=(12, 0, 0, 0))
        right.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Label(right, text="Vehicle Details", font=("Segoe UI", 11, "bold")).pack(anchor=tk.W)

        form = ttk.Frame(right)
        form.pack(fill=tk.X, pady=6)

        self.form_vars = {
            "plate": tk.StringVar(),
            "owner": tk.StringVar(),
            "owner_type": tk.StringVar(value="Teacher"),
            "vehicle_type": tk.StringVar(value="Car"),
            "color": tk.StringVar(),
            "notes": tk.StringVar(),
        }

        labels = [
            ("Plate Number:", "plate"),
            ("Owner Name:", "owner"),
            ("Owner Type:", "owner_type"),
            ("Vehicle Type:", "vehicle_type"),
            ("Color:", "color"),
            ("Notes:", "notes"),
        ]

        for i, (label, key) in enumerate(labels):
            ttk.Label(form, text=label).grid(row=i, column=0, sticky=tk.W, pady=3)
            if key == "owner_type":
                cb = ttk.Combobox(form, textvariable=self.form_vars[key],
                                  values=["Teacher", "Staff", "Visitor", "Student"], width=25, state="readonly")
                cb.grid(row=i, column=1, pady=3, padx=4)
            elif key == "vehicle_type":
                cb = ttk.Combobox(form, textvariable=self.form_vars[key],
                                  values=["Car", "Motorcycle", "SUV", "Van", "Bicycle", "Other"], width=25, state="readonly")
                cb.grid(row=i, column=1, pady=3, padx=4)
            else:
                ttk.Entry(form, textvariable=self.form_vars[key], width=28).grid(row=i, column=1, pady=3, padx=4)

        btn_frame = ttk.Frame(right)
        btn_frame.pack(fill=tk.X, pady=10)

        ttk.Button(btn_frame, text="Register Vehicle", command=self.add_vehicle).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="Update Selected", command=self.update_vehicle).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="Delete Selected", command=self.delete_vehicle).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="Clear Form", command=self.clear_form).pack(fill=tk.X, pady=2)

        self.selected_vehicle_id = None

    # ------------------------------------------------------------------
    # Entry / Exit Tab
    # ------------------------------------------------------------------
    def _build_entry_tab(self):
        # Quick entry form
        form = ttk.LabelFrame(self.tab_entry, text="Log Entry / Exit", padding=10)
        form.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(form, text="Plate Number:").grid(row=0, column=0, sticky=tk.W, pady=4)
        self.entry_plate_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.entry_plate_var, width=20).grid(row=0, column=1, pady=4, padx=6)

        ttk.Label(form, text="Owner Name (if new):").grid(row=0, column=2, sticky=tk.W, pady=4, padx=(12, 0))
        self.entry_owner_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.entry_owner_var, width=25).grid(row=0, column=3, pady=4, padx=6)

        btn_row = ttk.Frame(form)
        btn_row.grid(row=1, column=0, columnspan=4, pady=8)
        ttk.Button(btn_row, text="Log ENTRY (Time In)", command=self.log_entry).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_row, text="Log EXIT (Time Out)", command=self.log_exit).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_row, text="Clear", command=self.clear_entry_form).pack(side=tk.LEFT, padx=4)

        # Current logs list
        ttk.Label(self.tab_entry, text="Today's Entry / Exit Logs", font=("Segoe UI", 11, "bold")).pack(anchor=tk.W, pady=(8, 4))

        columns = ("log_id", "plate", "owner", "time_in", "time_out", "status")
        self.tree_logs = ttk.Treeview(self.tab_entry, columns=columns, show="headings", height=14)
        headers = ["Log ID", "Plate", "Owner", "Time In", "Time Out", "Status"]
        widths = [70, 110, 160, 130, 130, 80]
        for col, text, w in zip(columns, headers, widths):
            self.tree_logs.heading(col, text=text)
            self.tree_logs.column(col, width=w, anchor=tk.CENTER if col != "owner" else tk.W)
        self.tree_logs.pack(fill=tk.BOTH, expand=True)

    # ------------------------------------------------------------------
    # Reports Tab
    # ------------------------------------------------------------------
    def _build_reports_tab(self):
        btn_frame = ttk.Frame(self.tab_reports)
        btn_frame.pack(fill=tk.X, pady=(0, 6))

        ttk.Button(btn_frame, text="Currently Parked", command=lambda: self.show_report("parked")).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="Today's Logs", command=lambda: self.show_report("today")).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="All Registered Vehicles", command=lambda: self.show_report("vehicles")).pack(side=tk.LEFT, padx=3)

        self.report_text = tk.Text(self.tab_reports, height=25, wrap=tk.WORD, font=("Consolas", 10))
        self.report_text.pack(fill=tk.BOTH, expand=True)
        self.report_text.configure(state=tk.DISABLED)

    # ------------------------------------------------------------------
    # Refresh helpers
    # ------------------------------------------------------------------
    def refresh_all(self):
        self.refresh_vehicles()
        self.refresh_logs()
        self.update_status()
        self.show_report("parked")

    def update_status(self):
        total_vehicles = len(self.data["vehicles"])
        parked = sum(1 for log in self.data["logs"] if log["status"] == "Inside")
        today_logs = sum(1 for log in self.data["logs"] if log["time_in"].startswith(storage.today_str()))
        self.status_var.set(f"Registered: {total_vehicles}  |  Currently Parked: {parked}  |  Today's Logs: {today_logs}")

    def refresh_vehicles(self):
        for item in self.tree_vehicles.get_children():
            self.tree_vehicles.delete(item)
        query = self.search_var.get().strip().lower()
        for v in self.data["vehicles"]:
            if query:
                if query not in v["plate_number"].lower() and query not in v["owner_name"].lower():
                    continue
            self.tree_vehicles.insert("", tk.END, values=(
                v["vehicle_id"], v["plate_number"], v["owner_name"],
                v["owner_type"], v["vehicle_type"], v.get("color", "")
            ))

    def refresh_logs(self):
        for item in self.tree_logs.get_children():
            self.tree_logs.delete(item)
        today = storage.today_str()
        for log in reversed(self.data["logs"]):
            if log["time_in"].startswith(today) or log["status"] == "Inside":
                self.tree_logs.insert("", tk.END, values=(
                    log["log_id"], log["plate_number"], log["owner_name"],
                    log["time_in"], log.get("time_out") or "—", log["status"]
                ))

    # ------------------------------------------------------------------
    # Vehicle actions
    # ------------------------------------------------------------------
    def on_vehicle_select(self, event=None):
        selected = self.tree_vehicles.selection()
        if not selected:
            return
        values = self.tree_vehicles.item(selected[0], "values")
        vid = values[0]
        vehicle = next((v for v in self.data["vehicles"] if v["vehicle_id"] == vid), None)
        if not vehicle:
            return
        self.selected_vehicle_id = vid
        self.form_vars["plate"].set(vehicle["plate_number"])
        self.form_vars["owner"].set(vehicle["owner_name"])
        self.form_vars["owner_type"].set(vehicle["owner_type"])
        self.form_vars["vehicle_type"].set(vehicle["vehicle_type"])
        self.form_vars["color"].set(vehicle.get("color", ""))
        self.form_vars["notes"].set(vehicle.get("notes", ""))

    def clear_form(self):
        self.selected_vehicle_id = None
        for var in self.form_vars.values():
            var.set("")
        self.form_vars["owner_type"].set("Teacher")
        self.form_vars["vehicle_type"].set("Car")
        self.tree_vehicles.selection_remove(self.tree_vehicles.selection())

    def add_vehicle(self):
        plate = self.form_vars["plate"].get().strip().upper()
        owner = self.form_vars["owner"].get().strip()
        owner_type = self.form_vars["owner_type"].get()
        vehicle_type = self.form_vars["vehicle_type"].get()
        color = self.form_vars["color"].get().strip()
        notes = self.form_vars["notes"].get().strip()

        if not plate or not owner:
            messagebox.showwarning("Validation", "Plate Number and Owner Name are required.")
            return

        # Check duplicate plate
        if any(v["plate_number"].upper() == plate for v in self.data["vehicles"]):
            messagebox.showwarning("Validation", f"Plate number {plate} is already registered.")
            return

        new_vehicle = {
            "vehicle_id": storage.generate_vehicle_id(self.data),
            "plate_number": plate,
            "owner_name": owner,
            "owner_type": owner_type,
            "vehicle_type": vehicle_type,
            "color": color,
            "notes": notes
        }
        self.data["vehicles"].append(new_vehicle)
        storage.save_data(self.data)
        self.clear_form()
        self.refresh_all()
        messagebox.showinfo("Success", f"Vehicle {plate} registered successfully.")

    def update_vehicle(self):
        if not self.selected_vehicle_id:
            messagebox.showwarning("Selection", "Please select a vehicle first.")
            return

        vehicle = next((v for v in self.data["vehicles"] if v["vehicle_id"] == self.selected_vehicle_id), None)
        if not vehicle:
            return

        plate = self.form_vars["plate"].get().strip().upper()
        owner = self.form_vars["owner"].get().strip()
        if not plate or not owner:
            messagebox.showwarning("Validation", "Plate Number and Owner Name are required.")
            return

        # Check duplicate plate (exclude self)
        if any(v["plate_number"].upper() == plate and v["vehicle_id"] != self.selected_vehicle_id
               for v in self.data["vehicles"]):
            messagebox.showwarning("Validation", f"Plate number {plate} is already used by another vehicle.")
            return

        vehicle["plate_number"] = plate
        vehicle["owner_name"] = owner
        vehicle["owner_type"] = self.form_vars["owner_type"].get()
        vehicle["vehicle_type"] = self.form_vars["vehicle_type"].get()
        vehicle["color"] = self.form_vars["color"].get().strip()
        vehicle["notes"] = self.form_vars["notes"].get().strip()

        storage.save_data(self.data)
        self.clear_form()
        self.refresh_all()
        messagebox.showinfo("Success", "Vehicle updated successfully.")

    def delete_vehicle(self):
        if not self.selected_vehicle_id:
            messagebox.showwarning("Selection", "Please select a vehicle first.")
            return

        vehicle = next((v for v in self.data["vehicles"] if v["vehicle_id"] == self.selected_vehicle_id), None)
        if not vehicle:
            return

        if storage.is_currently_parked(self.data, vehicle["plate_number"]):
            messagebox.showwarning("Cannot Delete", "This vehicle is currently parked. Log an exit first.")
            return

        if not messagebox.askyesno("Confirm Delete", f"Delete vehicle {vehicle['plate_number']}?\nThis cannot be undone."):
            return

        self.data["vehicles"] = [v for v in self.data["vehicles"] if v["vehicle_id"] != self.selected_vehicle_id]
        storage.save_data(self.data)
        self.clear_form()
        self.refresh_all()
        messagebox.showinfo("Deleted", "Vehicle removed from registry.")

    # ------------------------------------------------------------------
    # Entry / Exit actions
    # ------------------------------------------------------------------
    def clear_entry_form(self):
        self.entry_plate_var.set("")
        self.entry_owner_var.set("")

    def log_entry(self):
        plate = self.entry_plate_var.get().strip().upper()
        if not plate:
            messagebox.showwarning("Validation", "Plate Number is required.")
            return

        if storage.is_currently_parked(self.data, plate):
            messagebox.showwarning("Already Inside", f"Vehicle {plate} is already logged as inside.")
            return

        # Find registered vehicle or use provided owner name
        vehicle = next((v for v in self.data["vehicles"] if v["plate_number"].upper() == plate), None)
        if vehicle:
            owner = vehicle["owner_name"]
            owner_type = vehicle["owner_type"]
        else:
            owner = self.entry_owner_var.get().strip()
            if not owner:
                messagebox.showwarning("Validation", "Vehicle not registered. Please enter Owner Name.")
                return
            owner_type = "Visitor"
            # Auto-register as visitor
            new_v = {
                "vehicle_id": storage.generate_vehicle_id(self.data),
                "plate_number": plate,
                "owner_name": owner,
                "owner_type": "Visitor",
                "vehicle_type": "Car",
                "color": "",
                "notes": "Auto-registered on entry"
            }
            self.data["vehicles"].append(new_v)

        log = {
            "log_id": storage.generate_log_id(self.data),
            "plate_number": plate,
            "owner_name": owner,
            "owner_type": owner_type,
            "time_in": storage.now_str(),
            "time_out": None,
            "status": "Inside"
        }
        self.data["logs"].append(log)
        storage.save_data(self.data)
        self.clear_entry_form()
        self.refresh_all()
        messagebox.showinfo("Entry Logged", f"{plate} ({owner}) entered at {log['time_in']}")

    def log_exit(self):
        plate = self.entry_plate_var.get().strip().upper()
        if not plate:
            messagebox.showwarning("Validation", "Plate Number is required.")
            return

        open_log = storage.get_open_log(self.data, plate)
        if not open_log:
            messagebox.showwarning("Not Inside", f"No open entry found for {plate}.")
            return

        open_log["time_out"] = storage.now_str()
        open_log["status"] = "Exited"
        storage.save_data(self.data)
        self.clear_entry_form()
        self.refresh_all()
        messagebox.showinfo("Exit Logged", f"{plate} exited at {open_log['time_out']}")

    # ------------------------------------------------------------------
    # Reports
    # ------------------------------------------------------------------
    def show_report(self, report_type):
        self.report_text.configure(state=tk.NORMAL)
        self.report_text.delete("1.0", tk.END)

        if report_type == "parked":
            lines = ["CURRENTLY PARKED VEHICLES", "=" * 50, ""]
            parked = [log for log in self.data["logs"] if log["status"] == "Inside"]
            if not parked:
                lines.append("No vehicles currently parked.")
            else:
                for log in parked:
                    lines.append(f"{log['log_id']}  |  {log['plate_number']}  –  {log['owner_name']}")
                    lines.append(f"   Type: {log.get('owner_type', '')}   Time In: {log['time_in']}")
                    lines.append("")
            lines.append(f"Total currently parked: {len(parked)}")

        elif report_type == "today":
            lines = ["TODAY'S ENTRY / EXIT LOGS", "=" * 50, ""]
            today = storage.today_str()
            today_logs = [log for log in self.data["logs"] if log["time_in"].startswith(today)]
            if not today_logs:
                lines.append("No logs recorded today.")
            else:
                for log in today_logs:
                    status = log["status"]
                    tout = log.get("time_out") or "—"
                    lines.append(f"{log['log_id']}  |  {log['plate_number']}  –  {log['owner_name']}")
                    lines.append(f"   In: {log['time_in']}   Out: {tout}   Status: {status}")
                    lines.append("")
            lines.append(f"Total logs today: {len(today_logs)}")

        else:  # vehicles
            lines = ["ALL REGISTERED VEHICLES", "=" * 50, ""]
            for v in sorted(self.data["vehicles"], key=lambda x: x["plate_number"]):
                lines.append(f"{v['vehicle_id']}  {v['plate_number']:<12}  {v['owner_name'][:25]:<25}  {v['owner_type']:<10}  {v['vehicle_type']}")
            lines.append("")
            lines.append(f"Total registered: {len(self.data['vehicles'])}")

        self.report_text.insert(tk.END, "\n".join(lines))
        self.report_text.configure(state=tk.DISABLED)


def main():
    root = tk.Tk()
    app = ParkingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
