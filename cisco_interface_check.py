from netmiko import ConnectHandler
import os

device = {
    "device_type": "cisco_ios",
    "host": os.environ.get("CISCO_HOST"),
    "username": os.environ.get("CISCO_USERNAME"),
    "password": os.environ.get("CISCO_PASSWORD"),
}

print("\nConnecting to Cisco device...")
connection = ConnectHandler(**device)

interface_output = connection.send_command("show ip interface brief")
version_output = connection.send_command("show version")

connection.disconnect()
print("Connection closed successfully.")

print("\n========== SHOW IP INTERFACE BRIEF ==========")
print(interface_output)

print("\n========== SHOW VERSION ==========")
print(version_output)

interface_lines = interface_output.splitlines()

print("\n========== LOOPBACK INTERFACE REPORT ==========")

operational_count = 0
loopback_count = 0

for line in interface_lines:
    if "Loopback" in line:
        loopback_count += 1

        fields = line.split()
        interface_name = fields[0]
        ip_address = fields[1]
        protocol_status = fields[-1]
        interface_status = " ".join(fields[4:-1])

        if interface_status == "up" and protocol_status == "up":
            operational_result = "OPERATIONAL"
            operational_count += 1
        else:
            operational_result = "CHECK REQUIRED"

        print(f"\nInterface Name : {interface_name}")
        print(f"IP Address     : {ip_address}")
        print(f"Status         : {interface_status}")
        print(f"Protocol       : {protocol_status}")
        print(f"Result         : {operational_result}")

print("\n========== COMMANDER'S SUMMARY ==========")
print(f"Cisco Device              : {device['host']}")
print(f"Loopback Interfaces Found : {loopback_count}")
print(f"Operational Interfaces    : {operational_count}")
print(f"Check Required Interfaces : {loopback_count - operational_count}")