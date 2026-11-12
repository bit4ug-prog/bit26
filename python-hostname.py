from netmiko import ConnectHandler

# Cisco switch connection details
switch = {
    "device_type": "cisco_ios",
    "host": "devnetsandboxiosxec9k.cisco.com",
    "username": "mohammed",
    "password": "!zoOHdp3I6$d5",
    "secret": "!zoOHdp3I6$d5"
}

# Connect to switch
connection = ConnectHandler(**switch)

print("Connected to Cisco Switch!")

# Enter enable mode
connection.enable()

# Configuration commands
commands = [
    "hostname BIT-CISCO-DEVNET-SWITCH",
    "interface vlan 1",
    "ip address 192.168.10.100 255.255.255.0",
    "no shutdown",
    "exit"
]

# Execute configuration
output = connection.send_config_set(commands)

print("\nConfiguration Output:")
print(output)

# Save configuration
connection.save_config()

print("\nConfiguration saved successfully!")

# Verify hostname and IP
print("\nHostname:")
print(connection.send_command("show running-config | include hostname"))

print("\nInterface IP:")
print(connection.send_command("show ip interface brief"))

# Disconnect
connection.disconnect()

print("\nAutomation completed!")