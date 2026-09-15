"""Day 1 multi-system check + Activity #6 error handling.
Keep the Lab #2 loop design. One failed system must not stop the rest.
"""

import os
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

systems = {
    "cisco": {
        "commands": ["show ip interface brief"],
        "connection": {
            "device_type": "cisco_ios",
            "host": os.getenv("CISCO_HOST"),
            "username": os.getenv("CISCO_USERNAME"),
            "password": os.getenv("CISCO_PASSWORD"),
            "secret": os.getenv("CISCO_ENABLE_SECRET"),
            "conn_timeout": 5,
        },
    },
    "linux": {
        "commands": ["ip -br addr"],
        "connection": {
            "device_type": "linux",
            "host": os.getenv("LINUX_HOST"),
            "username": os.getenv("LINUX_USERNAME"),
            "password": os.getenv("LINUX_PASSWORD"),
            "conn_timeout": 5,
        },
    },
}

for name, details in systems.items():
    print("=" * 50)
    print(f"Checking {name}")
    print("=" * 50)

    connection = None
    try:
        connection = ConnectHandler(**details["connection"])
        if details["connection"].get("secret"):
            connection.enable()
        for command in details["commands"]:
            print(f"\n--- {name} :: {command} ---")
            print(connection.send_command(command))

    except NetmikoTimeoutException:
        print(f"FAILED: {name} SSH connection timed out.")

    except NetmikoAuthenticationException:
        print(f"FAILED: {name} SSH authentication was not accepted.")

    finally:
        if connection:
            connection.disconnect()
