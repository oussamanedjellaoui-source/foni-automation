import os
from netmiko import ConnectHandler
from netmiko.exceptions import (
    NetmikoAuthenticationException,
    NetmikoTimeoutException,
)

devices = [
    {
        "name": "FONI-Cisco-01",
        "connection": {
            "device_type": "cisco_ios",
            "host": os.getenv("CISCO_HOST"),
            "username": os.getenv("CISCO_USERNAME"),
            "password": os.getenv("CISCO_PASSWORD"),
        },
        "commands": [
            "show ip interface brief",
            "show version",
            "show ip route",
        ],
    },
    {
        "name": "FONI-Linux-01",
        "connection": {
            "device_type": "linux",
            "host": os.getenv("LINUX_HOST"),
            "username": os.getenv("LINUX_USERNAME"),
            "password": os.getenv("LINUX_PASSWORD"),
        },
        "commands": [
            "ip -br addr",
            "uname -a",
            "ip route",
            "df -h",
        ],
    },
]

for device in devices:
    print(f"\n========== {device['name']} ==========")
    connection = None

    try:
        connection = ConnectHandler(**device["connection"])
    except NetmikoAuthenticationException:
        print(f"AUTH FAILED — {device['name']}")
        continue
    except NetmikoTimeoutException:
        print(f"TIMEOUT — {device['name']}")
        continue
    except Exception as error:
        print(f"CONNECTION ERROR — {device['name']}: {error}")
        continue

    try:
        for command in device["commands"]:
            print(f"\n----- {device['name']} :: {command} -----")
            print(connection.send_command(command))
    except Exception as error:
        print(f"COMMAND ERROR — {device['name']}: {error}")
    finally:
        if connection:
            connection.disconnect()
            print(f"Closed {device['name']}")