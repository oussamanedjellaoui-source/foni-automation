"""Day 2 server test + Activity #6 error handling."""

import os
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

device = {
    "device_type": "linux",
    "host": os.getenv("SERVER2_HOST"),
    "username": os.getenv("LINUX_USERNAME"),
    "password": os.getenv("LINUX_PASSWORD"),
    "conn_timeout": 5,
}

try:
    connection = ConnectHandler(**device)
    output = connection.send_command("ip -br addr")
    print(output)
    connection.disconnect()

except NetmikoTimeoutException:
    print("FAILED: SSH connection timed out.")

except NetmikoAuthenticationException:
    print("FAILED: SSH authentication was not accepted.")
