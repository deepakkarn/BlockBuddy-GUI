import json
from datetime import datetime
import os
import subprocess

CONFIG_FILE = "config.json"
HOSTS_PATH = "/etc/hosts"
REDIRECT_IP = "127.0.0.1"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def generate_entries(sites):
    entries = []
    for site in sites:
        entries.append(f"{REDIRECT_IP} {site}")
        entries.append(f"{REDIRECT_IP} www.{site}")
    return entries

def is_block_time(config):
    now = datetime.now()
    current_day = now.strftime('%a').upper()
    current_time = now.strftime('%H:%M')

    if current_day[:3] not in config["block_days"]:
        return False

    start = config["block_start"]
    end = config["block_end"]

    if start > end:  # Overnight block (e.g., 23:00 - 09:00)
        return current_time >= start or current_time <= end
    else:
        return start <= current_time <= end

def apply_block():
    config = load_config()
    if not is_block_time(config):
        print("✅ Not in block time.")
        return

    entries = generate_entries(config["websites"])

    with open(HOSTS_PATH, "r+") as file:
        content = file.read()
        for entry in entries:
            if entry not in content:
                file.write(f"\n{entry}")

    flush_dns()
    notify("🔒 BlockBuddy is active. Let’s stay focused.")
    print("🚫 Block applied.")

def remove_block():
    config = load_config()
    entries = generate_entries(config["websites"])

    with open(HOSTS_PATH, "r") as file:
        lines = file.readlines()

    with open(HOSTS_PATH, "w") as file:
        for line in lines:
            if not any(entry in line for entry in entries):
                file.write(line)

    flush_dns()
    notify("✅ All websites unblocked.")
    print("✅ Block removed.")

def flush_dns():
    os.system("sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder")

def notify(message):
    try:
        subprocess.run(['osascript', '-e', f'display notification "{message}" with title "BlockBuddy-GUI"'])
    except Exception as e:
        print(f"(Notification error: {e})")
