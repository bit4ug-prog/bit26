from netmiko import ConnectHandler
from getpass import getpass
import csv
import os
import time
from datetime import datetime

# NTP Configuration
OLD_NTP = "192.168.10.100"
NEW_NTP = "192.168.10.200"

# Read credentials securely
username = input("Enter Cisco username: ")
password = getpass("Enter Cisco password: ")

# Files and folders
INVENTORY = "switches.csv"
BACKUP_DIR = "backups"
REPORT = "ntp_report.csv"

os.makedirs(BACKUP_DIR, exist_ok=True)

# Report header
results = []

# Read switch inventory
with open(INVENTORY, "r") as file:
    switches = list(csv.DictReader(file))

print(f"\nTotal switches: {len(switches)}")
print("Starting NTP automation...\n")

for switch in switches:

    ip = switch["host"]
    device_type = switch["device_type"]

    print(f"\nConnecting to {ip}...")

    device = {
        "device_type": device_type,
        "host": ip,
        "username": username,
        "password": password,
        "timeout": 20,
        "conn_timeout": 15,
        "auth_timeout": 15,
        "banner_timeout": 20,
    }

    try:

        # Connect to Cisco switch
        net_connect = ConnectHandler(**device)

        print(f"Connected to {ip}")

        # Backup running configuration
        backup = net_connect.send_command(
            "show running-config"
        )

        backup_file = os.path.join(
            BACKUP_DIR,
            f"{ip.replace(':', '_')}.txt"
        )

        with open(backup_file, "w") as backup_file_handle:
            backup_file_handle.write(backup)

        print("Configuration backup completed")

        # Check existing NTP configuration
        ntp_config = net_connect.send_command(
            "show running-config | include ntp server"
        )

        print("Existing NTP configuration:")
        print(ntp_config)

        # Configure new NTP server
        commands = [
            f"no ntp server {OLD_NTP}",
            f"ntp server {NEW_NTP}"
        ]

        output = net_connect.send_config_set(commands)

        print("Configuration changes:")
        print(output)

        # Verify configuration
        verification = net_connect.send_command(
            "show running-config | include ntp server"
        )

        print("Verification:")
        print(verification)

        # Check configuration
        if (
            f"ntp server {NEW_NTP}" in verification
            and f"ntp server {OLD_NTP}" not in verification
        ):

            # Save configuration
            net_connect.save_config()

            status = "SUCCESS"

            print(f"{ip}: NTP updated successfully")

        else:

            status = "VERIFICATION FAILED"

            print(f"{ip}: NTP verification failed")

        # Disconnect
        net_connect.disconnect()

        results.append({
            "IP": ip,
            "Status": status,
            "Old_NTP": OLD_NTP,
            "New_NTP": NEW_NTP,
            "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    except Exception as error:

        print(f"Error connecting to {ip}: {error}")

        results.append({
            "IP": ip,
            "Status": f"FAILED: {error}",
            "Old_NTP": OLD_NTP,
            "New_NTP": NEW_NTP,
            "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    # Small delay between switches
    time.sleep(2)


# Generate final report
with open(REPORT, "w", newline="") as file:

    fieldnames = [
        "IP",
        "Status",
        "Old_NTP",
        "New_NTP",
        "Time"
    ]

    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(results)


print("\n================================")
print("NTP AUTOMATION COMPLETED")
print("================================")

print(f"Total switches: {len(switches)}")
print(f"Successful: {sum(1 for r in results if r['Status'] == 'SUCCESS')}")
print(f"Failed/Other: {sum(1 for r in results if r['Status'] != 'SUCCESS')}")

print(f"\nReport saved: {REPORT}")
print(f"Backups saved: {BACKUP_DIR}")