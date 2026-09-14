from getpass import getpass
from netmiko import ConnectHandler


# Cisco device information
device = {
    "device_type": "cisco_ios",
    "host": "54.90.112.247",
    "username": "onedjellaoui",
    "password": getpass("Cisco password: "),
}


# Connect to the Cisco device
print("\nConnecting to Cisco device...")

connection = ConnectHandler(**device)


# Collect information using authorized show commands
interface_output = connection.send_command(
    "show ip interface brief"
)

version_output = connection.send_command(
    "show version"
)


# Close the connection after collecting data
connection.disconnect()

print("Connection closed successfully.")


# Display original command output
print("\n========== SHOW IP INTERFACE BRIEF ==========")
print(interface_output)

print("\n========== SHOW VERSION ==========")
print(version_output)


# Step 4: Separate interface output into individual lines
interface_lines = interface_output.splitlines()

print("\n========== LOOPBACK INTERFACE REPORT ==========")

operational_count = 0
loopback_count = 0


# Step 5: Find Loopback interface lines
for line in interface_lines:
    if "Loopback" in line:

        loopback_count += 1

        # Step 6: Separate the line into individual fields
        fields = line.split()

        interface_name = fields[0]
        ip_address = fields[1]
        protocol_status = fields[-1]

        # Supports both "up" and "administratively down"
        interface_status = " ".join(fields[4:-1])

        # Step 7: Make the operational decision
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


# Final summary
print("\n========== COMMANDER'S SUMMARY ==========")
print(f"Cisco Device              : {device['host']}")
print(f"Loopback Interfaces Found : {loopback_count}")
print(f"Operational Interfaces    : {operational_count}")
print(f"Check Required Interfaces : {loopback_count - operational_count}")