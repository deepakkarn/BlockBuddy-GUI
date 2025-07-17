from version import __version__
import tkinter as tk
from tkinter import messagebox
import json
import blocker_engine  

CONFIG_FILE = "config.json"
DAYS = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]

def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "websites": [],
            "block_days": [],
            "block_start": "23:00",
            "block_end": "09:00"
        }

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)
    messagebox.showinfo("Saved", "Settings saved to config.json")
class BlockBuddyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"BlockBuddy-GUI v{__version__}")
        self.config = load_config()

        # --- Top: Site Entry & Add ---
        tk.Label(root, text="Website to Block:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.site_entry = tk.Entry(root, width=30)
        self.site_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        tk.Button(root, text="Add Site", command=self.add_site).grid(row=0, column=2, padx=5, pady=5)

        # --- Listbox + Remove ---
        self.site_listbox = tk.Listbox(root, height=5, width=50)
        self.site_listbox.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        tk.Button(root, text="Remove Selected", command=self.remove_site).grid(row=1, column=2, padx=5)

        # --- Time Inputs ---
        tk.Label(root, text="Start Time (HH:MM):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.start_time = tk.Entry(root)
        self.start_time.insert(0, self.config["block_start"])
        self.start_time.grid(row=2, column=1, padx=5, sticky="w")

        tk.Label(root, text="End Time (HH:MM):").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.end_time = tk.Entry(root)
        self.end_time.insert(0, self.config["block_end"])
        self.end_time.grid(row=3, column=1, padx=5, sticky="w")

        # --- Day Checkboxes ---
        tk.Label(root, text="Block Days:").grid(row=4, column=0, sticky="nw", padx=5)
        self.day_vars = {}
        day_frame = tk.Frame(root)
        day_frame.grid(row=4, column=1, columnspan=2, sticky="w", pady=5)
        for i, day in enumerate(DAYS):
            var = tk.BooleanVar(value=day in self.config["block_days"])
            cb = tk.Checkbutton(day_frame, text=day, variable=var)
            cb.grid(row=i // 4, column=i % 4, sticky="w", padx=4)
            self.day_vars[day] = var

        # --- Action Buttons ---
        action_frame = tk.Frame(root)
        action_frame.grid(row=5, column=0, columnspan=3, pady=10)

        tk.Button(action_frame, text="💾 Save Settings", command=self.save_settings).grid(row=0, column=0, padx=5)
        tk.Button(action_frame, text="🔒 Block Now", command=blocker_engine.apply_block).grid(row=0, column=1, padx=5)
        tk.Button(action_frame, text="✅ Unblock", command=blocker_engine.remove_block).grid(row=0, column=2, padx=5)
        tk.Button(action_frame, text="❌ Quit", command=self.root.quit).grid(row=0, column=3, padx=5)
        tk.Label(root, text=f"Version: {__version__}", fg="gray").grid(row=7, column=0, columnspan=3, pady=(0, 10))

        self.refresh_site_list()


    def add_site(self):
        site = self.site_entry.get().strip()
        if site and site not in self.config["websites"]:
            self.config["websites"].append(site)
            self.refresh_site_list()
            self.site_entry.delete(0, tk.END)

    def remove_site(self):
        selection = self.site_listbox.curselection()
        if selection:
            site = self.site_listbox.get(selection[0])
            self.config["websites"].remove(site)
            self.refresh_site_list()

    def refresh_site_list(self):
        self.site_listbox.delete(0, tk.END)
        for site in self.config["websites"]:
            self.site_listbox.insert(tk.END, site)

    def save_settings(self):
        self.config["block_start"] = self.start_time.get().strip()
        self.config["block_end"] = self.end_time.get().strip()
        self.config["block_days"] = [day for day, var in self.day_vars.items() if var.get()]
        save_config(self.config)

if __name__ == "__main__":
    root = tk.Tk()
    app = BlockBuddyGUI(root)
    root.mainloop()

