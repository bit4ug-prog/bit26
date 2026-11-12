from netmiko import ConnectHandler

# Cisco switch connection details
switch = {
    "device_type": "cisco_ios",
    "host": "devnetsandboxiosxec9k.cisco.com",
    "username": "mohammed",
    "password": "!zoOHdp3I6$d5",
    "secret": "!zoOHdp3I6$d5"
}

# Connect to Cisco Switch
connection = ConnectHandler(**switch)

print("Connected Successfully!")

# Change NTP Server
commands = [
    "no ntp server 10.17.251.250",
    "ntp server 192.168.10.200"
]

output = connection.send_config_set(commands)

print(output)

# Save Configuration
connection.save_config()

# Verify NTP
print("\nUpdated NTP Configuration:")
print(connection.send_command("show running-config | include ntp"))

connection.disconnect()

print("\nNTP Update Completed!")