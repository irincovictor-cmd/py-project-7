"""
School Parking and Vehicle Registration System
Redesigned interface – distinct from the Library system.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

import storage


class ParkingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("School Parking and Vehicle Registration System")
        self.root.geometry("1100x680")
        self.root.minsize(1000, 620)

        # Colors for a distinct look
        self.BG = "#1e293b"          # dark slate
        self.CARD = "#334155"        # card background
        self.ACCENT = "#38bdf8"      # sky blue accent
        self.TEXT = "#f1f5f9"        # light text
        self.MUTED = "#94a3b8"       # muted text
        self.SUCCESS = "#4ade80"
        self.WARNING = "#fbbf24"

        self.root.configure(bg=self.BG)
        self.data = storage.load_data()

        self._setup_styles()
        self._build_ui()
        self.refresh_all()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Treeview",
                        background="#0f172a",
                        foreground=self.TEXT,
                        fieldbackground="#0f172a",
                        rowheight=28,
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading",
                        background="#1e293b",
                        foreground=self.ACCENT,
                        font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", "#0369a1")])

    def _build_ui(self):
        # ===== TOP HEADER =====
        header = tk.Frame(self.root, bg=self.BG, height=70)
        header.pack(fill=tk.X, padx=16, pady=(12, 8))
        header.pack_propagate(False)

        tk.Label(header, text="PARKING CONTROL", bg=self.BG, fg=self.ACCENT,
                 font=("Segoe UI", 20, "bold")).pack(side=tk.LEFT, pady=12)

        self.status_var = tk.StringVar()
        tk.Label(header, textvariable=self.status_var, bg=self.BG, fg=self.MUTED,
                 font=("Segoe UI", 11)).pack(side=tk.RIGHT, pady=18)

        # ===== DASHBOARD CARDS =====
        cards_frame = tk.Frame(self.root, bg=self.BG)
        cards_frame.pack(fill=tk.X, padx=16, pady=(0, 10))

        self.card_registered = self._make_stat_card(cards_frame, "REGISTERED", "0")
        self.card_parked = self._make_stat_card(cards_frame, "CURRENTLY PARKED", "0")
        self.card_today = self._make_stat_card(cards_frame, "TODAY'S LOGS", "0")

        self.card_registered.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self.card_parked.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        self.card_today.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))

        # ===== MAIN CONTENT (left nav + right content) =====
        main = tk.Frame(self.root, bg=self.BG)
        main.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 12))

        # Left navigation
        nav = tk.Frame(main, bg=self.CARD, width=180)
        nav.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))
        nav.pack_propagate(False)

        tk.Label(nav, text="MENU", bg=self.CARD, fg=self.MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, padx=16, pady=(16, 8))

        self.nav_buttons = {}
        for key, label in [
            ("dashboard", "Dashboard"),
            ("registry", "Vehicle Registry"),
            ("entry", "Entry / Exit"),
            ("reports", "Reports"),
        ]:
            btn = tk.Button(
                nav, text=label, bg=self.CARD, fg=self.TEXT,
                activebackground="#475569", activeforeground=self.TEXT,
                font=("Segoe UI", 11), relief=tk.FLAT, anchor="w",
                padx=16, pady=10, cursor="hand2",
                command=lambda k=key: self.show_page(k)
            )
            btn.pack(fill=tk.X)
            self.nav_buttons[key] = btn

        # Right content area
        self.content = tk.Frame(main, bg=self.BG)
        self.content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Build pages
        self.pages = {}
        self._build_dashboard_page()
        self._build_registry_page()
        self._build_entry_page()
        self._build_reports_page()

        self.show_page("dashboard")

    def _make_stat_card(self, parent, title, value):
        card = tk.Frame(parent, bg=self.CARD, padx=16, pady=12)
        tk.Label(card, text=title, bg=self.CARD, fg=self.MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor=tk.W)
        val_label = tk.Label(card, text=value, bg=self.CARD, fg=self.ACCENT,
                             font=("Segoe UI", 26, "bold"))
        val_label.pack(anchor=tk.W, pady=(4, 0))
        card.value_label = val_label
        return card

    def show_page(self, key):
        for page in self.pages.values():
            page.pack_forget()
        self.pages[key].pack(fill=tk.BOTH, expand=True)

        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.configure(bg="#0369a1", fg="white")
            else:
                btn.configure(bg=self.CARD, fg=self.TEXT)

    def _build_dashboard_page(self):
        page = tk.Frame(self.content, bg=self.BG)
        self.pages["dashboard"] = page

        tk.Label(page, text="Quick Entry / Exit", bg=self.BG, fg=self.TEXT,
                 font=("Segoe UI", 14, "bold")).pack(anchor=tk.W, pady=(0, 8))

        form = tk.Frame(page, bg=self.CARD, padx=16, pady=14)
        form.pack(fill=tk.X, pady=(0, 12))

        tk.Label(form, text="Plate Number", bg=self.CARD, fg=self.MUTED,
                 font=("Segoe UI", 9)).grid(row=0, column=0, sticky=tk.W)
        self.dash_plate = tk.StringVar()
        tk.Entry(form, textvariable=self.dash_plate, width=18, bg="#0f172a", fg=self.TEXT,
                 insertbackground=self.TEXT, font=("Segoe UI", 12), relief=tk.FLAT).grid(row=1, column=0, padx=(0, 12), pady=4)

        tk.Label(form, text="Owner (if new visitor)", bg=self.CARD, fg=self.MUTED,
                 font=("Segoe UI", 9)).grid(row=0, column=1, sticky=tk.W)
        self.dash_owner = tk.StringVar()
        tk.Entry(form, textvariable=self.dash_owner, width=22, bg="#0f172a", fg=self.TEXT,
                 insertbackground=self.TEXT, font=("Segoe UI", 12), relief=tk.FLAT).grid(row=1, column=1, padx=(0, 12), pady=4)

        btn_frame = tk.Frame(form, bg=self.CARD)
        btn_frame.grid(row=1, column=2, padx=8)
        tk.Button(btn_frame, text="  ENTRY  ", bg=self.SUCCESS, fg="#0f172a",
                  font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=12, pady=6,
                  command=self.dash_entry).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_frame, text="  EXIT  ", bg=self.WARNING, fg="#0f172a",
                  font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=12, pady=6,
                  command=self.dash_exit).pack(side=tk.LEFT, padx=4)

        tk.Label(page, text="Currently Parked", bg=self.BG, fg=self.TEXT,
                 font=("Segoe UI", 14, "bold")).pack(anchor=tk.W, pady=(8, 6))

        cols = ("plate", "owner", "type", "time_in")
        self.dash_tree = ttk.Treeview(page, columns=cols, show="headings", height=12)
        for col, text, w in zip(cols, ["Plate Number", "Owner", "Type", "Time In"], [140, 220, 120, 160]):
            self.dash_tree.heading(col, text=text)
            self.dash_tree.column(col, width=w, anchor=tk.CENTER if col != "owner" else tk.W)
        self.dash_tree.pack(fill=tk.BOTH, expand=True)

    def dash_entry(self):
        self.entry_plate_var.set(self.dash_plate.get())
        self.entry_owner_var.set(self.dash_owner.get())
        self.log_entry()
        self.dash_plate.set("")
        self.dash_owner.set("")

    def dash_exit(self):
        self.entry_plate_var.set(self.dash_plate.get())
        self.log_exit()
        self.dash_plate.set("")
        self.dash_owner.set("")

    def _build_registry_page(self):
        page = tk.Frame(self.content, bg=self.BG)
        self.pages["registry"] = page

        top = tk.Frame(page, bg=self.BG)
        top.pack(fill=tk.X, pady=(0, 8))

        tk.Label(top, text="Search:", bg=self.BG, fg=self.MUTED).pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh_vehicles())
        tk.Entry(top, textvariable=self.search_var, width=30, bg="#0f172a", fg=self.TEXT,
                 insertbackground=self.TEXT, relief=tk.FLAT, font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=8)

        tk.Button(top, text="Register New", bg=self.ACCENT, fg="#0f172a",
                  font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=10, pady=4,
                  command=self.open_register_dialog).pack(side=tk.RIGHT, padx=4)
        tk.Button(top, text="Delete Selected", bg="#475569", fg=self.TEXT,
                  font=("Segoe UI", 10), relief=tk.FLAT, padx=10, pady=4,
                  command=self.delete_vehicle).pack(side=tk.RIGHT, padx=4)

        cols = ("vehicle_id", "plate", "owner", "owner_type", "vehicle_type", "color")
        self.tree_vehicles = ttk.Treeview(page, columns=cols, show="headings", height=18)
        for col, text, w in zip(cols,
                                ["ID", "Plate", "Owner", "Owner Type", "Vehicle", "Color"],
                                [60, 120, 180, 110, 110, 90]):
            self.tree_vehicles.heading(col, text=text)
            self.tree_vehicles.column(col, width=w, anchor=tk.CENTER if col != "owner" else tk.W)
        self.tree_vehicles.pack(fill=tk.BOTH, expand=True)
        self.tree_vehicles.bind("<Double-1>", lambda e: self.open_edit_dialog())

    def open_register_dialog(self):
        self._vehicle_dialog(None)

    def open_edit_dialog(self):
        selected = self.tree_vehicles.selection()
        if not selected:
            return
        vid = self.tree_vehicles.item(selected[0], "values")[0]
        vehicle = next((v for v in self.data["vehicles"] if v["vehicle_id"] == vid), None)
        if vehicle:
            self._vehicle_dialog(vehicle)

    def _vehicle_dialog(self, vehicle):
        dlg = tk.Toplevel(self.root)
        dlg.title("Register Vehicle" if vehicle is None else "Edit Vehicle")
        dlg.geometry("400x380")
        dlg.configure(bg=self.BG)
        dlg.transient(self.root)
        dlg.grab_set()

        fields = {}
        labels = [
            ("Plate Number", "plate"),
            ("Owner Name", "owner"),
            ("Owner Type", "owner_type"),
            ("Vehicle Type", "vehicle_type"),
            ("Color", "color"),
            ("Notes", "notes"),
        ]

        for i, (label, key) in enumerate(labels):
            tk.Label(dlg, text=label, bg=self.BG, fg=self.MUTED,
                     font=("Segoe UI", 9)).grid(row=i, column=0, sticky=tk.W, padx=16, pady=(10, 2))
            if key == "owner_type":
                var = tk.StringVar(value=vehicle["owner_type"] if vehicle else "Teacher")
                cb = ttk.Combobox(dlg, textvariable=var,
                                  values=["Teacher", "Staff", "Visitor", "Student"],
                                  state="readonly", width=28)
                cb.grid(row=i, column=1, padx=16, pady=(10, 2))
            elif key == "vehicle_type":
                var = tk.StringVar(value=vehicle["vehicle_type"] if vehicle else "Car")
                cb = ttk.Combobox(dlg, textvariable=var,
                                  values=["Car", "Motorcycle", "SUV", "Van", "Bicycle", "Other"],
                                  state="readonly", width=28)
                cb.grid(row=i, column=1, padx=16, pady=(10, 2))
            else:
                default = ""
                if vehicle:
                    if key == "plate":
                        default = vehicle["plate_number"]
                    elif key == "owner":
                        default = vehicle["owner_name"]
                    else:
                        default = vehicle.get(key, "")
                var = tk.StringVar(value=default)
                tk.Entry(dlg, textvariable=var, width=30, bg="#0f172a", fg=self.TEXT,
                         insertbackground=self.TEXT, relief=tk.FLAT).grid(row=i, column=1, padx=16, pady=(10, 2))
            fields[key] = var

        def save():
            plate = fields["plate"].get().strip().upper()
            owner = fields["owner"].get().strip()
            if not plate or not owner:
                messagebox.showwarning("Validation", "Plate Number and Owner Name are required.", parent=dlg)
                return

            if vehicle is None:
                if any(v["plate_number"].upper() == plate for v in self.data["vehicles"]):
                    messagebox.showwarning("Validation", f"Plate {plate} already registered.", parent=dlg)
                    return
                new_v = {
                    "vehicle_id": storage.generate_vehicle_id(self.data),
                    "plate_number": plate,
                    "owner_name": owner,
                    "owner_type": fields["owner_type"].get(),
                    "vehicle_type": fields["vehicle_type"].get(),
                    "color": fields["color"].get().strip(),
                    "notes": fields["notes"].get().strip()
                }
                self.data["vehicles"].append(new_v)
                msg = f"Vehicle {plate} registered."
            else:
                if any(v["plate_number"].upper() == plate and v["vehicle_id"] != vehicle["vehicle_id"]
                       for v in self.data["vehicles"]):
                    messagebox.showwarning("Validation", f"Plate {plate} already used.", parent=dlg)
                    return
                vehicle["plate_number"] = plate
                vehicle["owner_name"] = owner
                vehicle["owner_type"] = fields["owner_type"].get()
                vehicle["vehicle_type"] = fields["vehicle_type"].get()
                vehicle["color"] = fields["color"].get().strip()
                vehicle["notes"] = fields["notes"].get().strip()
                msg = "Vehicle updated."

            storage.save_data(self.data)
            self.refresh_all()
            dlg.destroy()
            messagebox.showinfo("Success", msg)

        tk.Button(dlg, text="Save", bg=self.ACCENT, fg="#0f172a",
                  font=("Segoe UI", 11, "bold"), relief=tk.FLAT, padx=20, pady=8,
                  command=save).grid(row=6, column=0, columnspan=2, pady=20)

    def _build_entry_page(self):
        page = tk.Frame(self.content, bg=self.BG)
        self.pages["entry"] = page

        form = tk.Frame(page, bg=self.CARD, padx=16, pady=14)
        form.pack(fill=tk.X, pady=(0, 12))

        tk.Label(form, text="Plate Number", bg=self.CARD, fg=self.MUTED).grid(row=0, column=0, sticky=tk.W)
        self.entry_plate_var = tk.StringVar()
        tk.Entry(form, textvariable=self.entry_plate_var, width=18, bg="#0f172a", fg=self.TEXT,
                 insertbackground=self.TEXT, font=("Segoe UI", 12), relief=tk.FLAT).grid(row=1, column=0, padx=(0, 12))

        tk.Label(form, text="Owner (new visitor only)", bg=self.CARD, fg=self.MUTED).grid(row=0, column=1, sticky=tk.W)
        self.entry_owner_var = tk.StringVar()
        tk.Entry(form, textvariable=self.entry_owner_var, width=22, bg="#0f172a", fg=self.TEXT,
                 insertbackground=self.TEXT, font=("Segoe UI", 12), relief=tk.FLAT).grid(row=1, column=1, padx=(0, 12))

        btn_row = tk.Frame(form, bg=self.CARD)
        btn_row.grid(row=1, column=2)
        tk.Button(btn_row, text="  LOG ENTRY  ", bg=self.SUCCESS, fg="#0f172a",
                  font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=10, pady=6,
                  command=self.log_entry).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_row, text="  LOG EXIT  ", bg=self.WARNING, fg="#0f172a",
                  font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=10, pady=6,
                  command=self.log_exit).pack(side=tk.LEFT, padx=4)

        tk.Label(page, text="Recent Logs (Today + Currently Inside)", bg=self.BG, fg=self.TEXT,
                 font=("Segoe UI", 12, "bold")).pack(anchor=tk.W, pady=(4, 6))

        cols = ("log_id", "plate", "owner", "time_in", "time_out", "status")
        self.tree_logs = ttk.Treeview(page, columns=cols, show="headings", height=14)
        for col, text, w in zip(cols,
                                ["Log ID", "Plate", "Owner", "Time In", "Time Out", "Status"],
                                [70, 110, 180, 140, 140, 80]):
            self.tree_logs.heading(col, text=text)
            self.tree_logs.column(col, width=w, anchor=tk.CENTER if col != "owner" else tk.W)
        self.tree_logs.pack(fill=tk.BOTH, expand=True)

    def _build_reports_page(self):
        page = tk.Frame(self.content, bg=self.BG)
        self.pages["reports"] = page

        btn_frame = tk.Frame(page, bg=self.BG)
        btn_frame.pack(fill=tk.X, pady=(0, 8))

        for text, cmd in [
            ("Currently Parked", lambda: self.show_report("parked")),
            ("Today's Logs", lambda: self.show_report("today")),
            ("All Vehicles", lambda: self.show_report("vehicles")),
        ]:
            tk.Button(btn_frame, text=text, bg="#475569", fg=self.TEXT,
                      font=("Segoe UI", 10), relief=tk.FLAT, padx=12, pady=6,
                      command=cmd).pack(side=tk.LEFT, padx=4)

        self.report_text = tk.Text(page, height=24, wrap=tk.WORD, font=("Consolas", 11),
                                   bg="#0f172a", fg=self.TEXT, insertbackground=self.TEXT,
                                   relief=tk.FLAT, padx=12, pady=12)
        self.report_text.pack(fill=tk.BOTH, expand=True)
        self.report_text.configure(state=tk.DISABLED)

    def refresh_all(self):
        self.refresh_vehicles()
        self.refresh_logs()
        self.refresh_dashboard()
        self.update_status()
        self.show_report("parked")

    def update_status(self):
        total = len(self.data["vehicles"])
        parked = sum(1 for log in self.data["logs"] if log["status"] == "Inside")
        today = sum(1 for log in self.data["logs"] if log["time_in"].startswith(storage.today_str()))
        self.status_var.set(f"Registered {total}   |   Parked {parked}   |   Today {today}")
        self.card_registered.value_label.config(text=str(total))
        self.card_parked.value_label.config(text=str(parked))
        self.card_today.value_label.config(text=str(today))

    def refresh_vehicles(self):
        for item in self.tree_vehicles.get_children():
            self.tree_vehicles.delete(item)
        query = self.search_var.get().strip().lower()
        for v in self.data["vehicles"]:
            if query and query not in v["plate_number"].lower() and query not in v["owner_name"].lower():
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

    def refresh_dashboard(self):
        for item in self.dash_tree.get_children():
            self.dash_tree.delete(item)
        for log in self.data["logs"]:
            if log["status"] == "Inside":
                self.dash_tree.insert("", tk.END, values=(
                    log["plate_number"], log["owner_name"],
                    log.get("owner_type", ""), log["time_in"]
                ))

    def delete_vehicle(self):
        selected = self.tree_vehicles.selection()
        if not selected:
            messagebox.showwarning("Selection", "Select a vehicle first.")
            return
        vid = self.tree_vehicles.item(selected[0], "values")[0]
        vehicle = next((v for v in self.data["vehicles"] if v["vehicle_id"] == vid), None)
        if not vehicle:
            return
        if storage.is_currently_parked(self.data, vehicle["plate_number"]):
            messagebox.showwarning("Cannot Delete", "Vehicle is currently parked. Log exit first.")
            return
        if not messagebox.askyesno("Confirm", f"Delete {vehicle['plate_number']}?"):
            return
        self.data["vehicles"] = [v for v in self.data["vehicles"] if v["vehicle_id"] != vid]
        storage.save_data(self.data)
        self.refresh_all()
        messagebox.showinfo("Deleted", "Vehicle removed.")

    def log_entry(self):
        plate = self.entry_plate_var.get().strip().upper()
        if not plate:
            messagebox.showwarning("Validation", "Plate Number is required.")
            return
        if storage.is_currently_parked(self.data, plate):
            messagebox.showwarning("Already Inside", f"{plate} is already inside.")
            return

        vehicle = next((v for v in self.data["vehicles"] if v["plate_number"].upper() == plate), None)
        if vehicle:
            owner = vehicle["owner_name"]
            owner_type = vehicle["owner_type"]
        else:
            owner = self.entry_owner_var.get().strip()
            if not owner:
                messagebox.showwarning("Validation", "New vehicle – please enter Owner Name.")
                return
            owner_type = "Visitor"
            self.data["vehicles"].append({
                "vehicle_id": storage.generate_vehicle_id(self.data),
                "plate_number": plate,
                "owner_name": owner,
                "owner_type": "Visitor",
                "vehicle_type": "Car",
                "color": "",
                "notes": "Auto-registered on entry"
            })

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
        self.entry_plate_var.set("")
        self.entry_owner_var.set("")
        self.refresh_all()
        messagebox.showinfo("Entry Logged", f"{plate} entered at {log['time_in']}")

    def log_exit(self):
        plate = self.entry_plate_var.get().strip().upper()
        if not plate:
            messagebox.showwarning("Validation", "Plate Number is required.")
            return
        open_log = storage.get_open_log(self.data, plate)
        if not open_log:
            messagebox.showwarning("Not Inside", f"No open entry for {plate}.")
            return
        open_log["time_out"] = storage.now_str()
        open_log["status"] = "Exited"
        storage.save_data(self.data)
        self.entry_plate_var.set("")
        self.entry_owner_var.set("")
        self.refresh_all()
        messagebox.showinfo("Exit Logged", f"{plate} exited at {open_log['time_out']}")

    def show_report(self, report_type):
        self.report_text.configure(state=tk.NORMAL)
        self.report_text.delete("1.0", tk.END)

        if report_type == "parked":
            lines = ["CURRENTLY PARKED VEHICLES", "=" * 45, ""]
            parked = [l for l in self.data["logs"] if l["status"] == "Inside"]
            if not parked:
                lines.append("No vehicles currently parked.")
            else:
                for log in parked:
                    lines.append(f"{log['plate_number']:<12}  {log['owner_name']:<22}  In: {log['time_in']}")
            lines.append(f"\nTotal: {len(parked)}")

        elif report_type == "today":
            lines = ["TODAY'S LOGS", "=" * 45, ""]
            today = storage.today_str()
            logs = [l for l in self.data["logs"] if l["time_in"].startswith(today)]
            if not logs:
                lines.append("No logs today.")
            else:
                for log in logs:
                    tout = log.get("time_out") or "—"
                    lines.append(f"{log['plate_number']:<12}  {log['owner_name']:<20}  {log['time_in']} → {tout}  [{log['status']}]")
            lines.append(f"\nTotal: {len(logs)}")

        else:
            lines = ["ALL REGISTERED VEHICLES", "=" * 45, ""]
            for v in sorted(self.data["vehicles"], key=lambda x: x["plate_number"]):
                lines.append(f"{v['plate_number']:<12}  {v['owner_name'][:22]:<22}  {v['owner_type']:<10}  {v['vehicle_type']}")
            lines.append(f"\nTotal: {len(self.data['vehicles'])}")

        self.report_text.insert(tk.END, "\n".join(lines))
        self.report_text.configure(state=tk.DISABLED)


def main():
    root = tk.Tk()
    app = ParkingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
