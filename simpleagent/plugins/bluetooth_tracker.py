import asyncio
import json
from bleak import BleakScanner
from datetime import datetime, timedelta, timezone
import os
from modules.notifier import Notifier

def create_fingerprint(device_data: dict) -> str:
    """
    Creates a stable fingerprint from device advertisement data to identify a device
    even if its MAC address changes. It's based on manufacturer data and advertised services.
    """
    # Manufacturer IDs are a strong signal of device type
    mfr_ids = sorted(list(device_data.get("manufacturer_data", {}).keys()))

    # Service UUIDs also help define the device's capabilities
    uuids = sorted(device_data.get("service_uuids", []))

    # The combination of these, sorted to ensure consistency, forms the fingerprint.
    fingerprint_tuple = (tuple(mfr_ids), tuple(uuids))

    # We use the string representation of the tuple as a dictionary key.
    return str(fingerprint_tuple)

async def scan_devices():
    """Scans for Bluetooth devices and returns a dictionary of them."""
    devices = await BleakScanner.discover(return_adv=True)
    found_devices = {}
    for d, adv in devices.values():
        name = d.name if d.name else "Unknown Device"
        found_devices[d.address] = {
            "name": name,
            "address": d.address,
            "rssi": adv.rssi,
            "manufacturer_data": {comp_id: data.hex() for comp_id, data in adv.manufacturer_data.items()} if adv.manufacturer_data else {},
            "service_data": {uuid: data.hex() for uuid, data in adv.service_data.items()} if adv.service_data else {},
            "service_uuids": adv.service_uuids if adv.service_uuids else [],
        }
    return found_devices

def load_knowledge_base(kb_file):
    """Loads the device knowledge base from a JSON file."""
    if not os.path.exists(kb_file):
        return None
    try:
        with open(kb_file, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None # Return None to indicate a problem or empty file

def save_knowledge_base(kb_file, data):
    """Saves the device knowledge base to a JSON file."""
    try:
        with open(kb_file, 'w') as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        print(f"Error saving knowledge base file: {e}")

def log_scan_results(log_file, devices):
    """Logs all found devices to a file in a human-readable format."""
    timestamp = datetime.now().astimezone().isoformat()
    try:
        with open(log_file, 'a') as f:
            f.write(f"--- Scan at {timestamp} ---\n")
            if not devices:
                f.write("No devices found.\n\n")
                return

            f.write(f"{'Name':<30} | {'Address':<20} | {'RSSI':>5} | {'Fingerprint Components'}\n")
            f.write("-" * 120 + "\n")

            for device in devices.values():
                name = device['name']
                address = device['address']
                rssi = device['rssi']
                mfr_ids = sorted(list(device.get("manufacturer_data", {}).keys()))
                uuids = sorted(device.get("service_uuids", []))
                f.write(f"{name[:30]:<30} | {address:<20} | {rssi:>5} | Mfr IDs: {mfr_ids}, UUIDs: {uuids}\n")
            f.write("\n")
    except IOError as e:
        print(f"Error writing to scan log: {e}")

def initialize_knowledge_base():
    """Creates a new, empty knowledge base structure."""
    print("No existing knowledge base found. Starting in learning mode.")
    return {
        "plugin_mode": "learning",
        "learning_start_time": datetime.now().astimezone().isoformat(),
        "total_scans_in_learning_phase": 0,
        "devices": {}
    }

async def run(config: dict):
    """
    Main plugin function to learn regular Bluetooth devices and notify on anomalies.
    """
    task_config = config['tasks']['bluetooth_tracker']
    notifier = Notifier(config)

    # Load configuration
    kb_file = task_config.get('knowledge_base_file')
    log_file = task_config.get('scan_log_file')
    learning_hours = task_config.get('learning_duration_hours', 4)
    regularity_threshold = task_config.get('regularity_threshold', 0.7)
    ignore_list = task_config.get('ignore_list') or []

    if not all([kb_file, log_file]):
        print("Error: bluetooth_tracker task is not configured correctly. Ensure 'knowledge_base_file' and 'scan_log_file' are set.")
        return

    # Load or initialize the knowledge base
    kb = load_knowledge_base(kb_file)
    if kb is None:
        kb = initialize_knowledge_base()

    # Perform scan and log results
    print("Scanning for Bluetooth devices...")
    found_devices = await scan_devices()
    print(f"Scan complete. Found {len(found_devices)} devices.")
    log_scan_results(log_file, found_devices)

    # --- Update knowledge base with current scan ---
    now = datetime.now().astimezone()
    now_iso = now.isoformat()

    for address, device_data in found_devices.items():
        fingerprint = create_fingerprint(device_data)

        if fingerprint not in kb['devices']:
            # This is a new fingerprint
            kb['devices'][fingerprint] = {
                "name": device_data['name'],
                "addresses": {address: now_iso},
                "seen_count": 0,
                "first_seen": now_iso,
                "is_regular": False,
                "last_rssi": device_data['rssi'],
                "fingerprint_data": {
                    "manufacturer_data_keys": sorted(list(device_data.get("manufacturer_data", {}).keys())),
                    "service_uuids": sorted(device_data.get("service_uuids", []))
                }
            }

        kb_device = kb['devices'][fingerprint]
        # Update name if it was "Unknown" and we found a better one
        if kb_device['name'] == "Unknown Device" and device_data['name'] != "Unknown Device":
            kb_device['name'] = device_data['name']

        kb_device['seen_count'] += 1
        kb_device['last_seen'] = now_iso
        kb_device['addresses'][address] = now_iso # Add or update address
        kb_device['last_rssi'] = device_data['rssi']

    # --- Main Logic: Learning vs. Monitoring ---
    if kb['plugin_mode'] == 'learning':
        kb['total_scans_in_learning_phase'] += 1
        start_time = datetime.fromisoformat(kb['learning_start_time'])
        learning_duration = timedelta(hours=learning_hours)

        if now >= start_time + learning_duration:
            print("Learning phase complete. Calculating baseline of regular devices...")
            total_scans = kb['total_scans_in_learning_phase']
            regular_device_count = 0
            
            if total_scans > 0:
                for address, device in kb['devices'].items():
                    presence_ratio = device['seen_count'] / total_scans
                    if presence_ratio >= regularity_threshold:
                        device['is_regular'] = True
                        regular_device_count += 1
            
            kb['plugin_mode'] = 'monitoring'
            msg = f"Bluetooth tracker is now in monitoring mode. Identified {regular_device_count} regular devices."
            print(msg)
            notifier.send(msg)
        else:
            elapsed = now - start_time
            print(f"In learning mode. Scan {kb['total_scans_in_learning_phase']}. Time elapsed: {str(elapsed).split('.')[0]}/{learning_duration}")

    elif kb['plugin_mode'] == 'monitoring':
        print("In monitoring mode. Checking for unexpected devices...")
        reported_fingerprints = set()

        for address, device_data in found_devices.items():
            if address in ignore_list or device_data['name'] in ignore_list:
                continue

            fingerprint = create_fingerprint(device_data)
            if fingerprint in reported_fingerprints:
                continue

            is_known_regular = kb['devices'].get(fingerprint, {}).get('is_regular', False)

            if not is_known_regular:
                known_name = kb['devices'].get(fingerprint, {}).get('name', device_data.get('name', 'Unknown Device'))
                msg = f"Unexpected device detected: '{known_name}' (current address: {address})."
                print(f"NOTIFICATION: {msg}")
                notifier.send(msg)
                reported_fingerprints.add(fingerprint)

    # Save the updated knowledge base
    save_knowledge_base(kb_file, kb)
    print("Knowledge base updated.")

if __name__ == '__main__':
    # This is for standalone testing of the plugin.
    mock_config = {
        "notification_preference": ["ntfy"],
        "tasks": {
            "bluetooth_tracker": {
                'learning_duration_hours': 0.05, # Short duration for testing
                'regularity_threshold': 0.5,
                'ignore_list': [],
                'knowledge_base_file': ".bluetooth_knowledge_base.json",
                'scan_log_file': "bluetooth_scans.log"
            }
        }
    }
    # Clean up old files for a fresh test run
    if os.path.exists(".bluetooth_knowledge_base.json"):
        os.remove(".bluetooth_knowledge_base.json")
    asyncio.run(run(mock_config))
