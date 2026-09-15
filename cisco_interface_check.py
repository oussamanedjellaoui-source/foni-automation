"""Day 1 Cisco interface check + Activity #6 error handling.
Keep the same authorized read-only commands from Lab #1.
"""

import os
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

device = {
    "device_type": "cisco_ios",
    "host": os.getenv("CISCO_HOST"),
    "username": os.getenv("CISCO_USERNAME"),
    "password": os.getenv("CISCO_PASSWORD"),
    "secret": os.getenv("CISCO_ENABLE_SECRET"),
    "conn_timeout": 5,
}

try:
    connection = ConnectHandler(**device)
    if device.get("secret"):
        connection.enable()

    print("=== show ip interface brief ===")
    print(connection.send_command("show ip interface brief"))

    print("\n=== show version ===")
    print(connection.send_command("show version"))

    connection.disconnect()

except NetmikoTimeoutException:
    print("FAILED: SSH connection timed out.")

except NetmikoAuthenticationException:
    print("FAILED: SSH authentication was not accepted.")
