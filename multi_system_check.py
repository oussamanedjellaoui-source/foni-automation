import os
from netmiko import ConnectHandler
devices = [
    {
        "name": "cisco-c8000v",
        "device_type": "cisco_ios",
        "host": os.environ.get("CISCO_HOST"),
        "username": os.environ.get("CISCO_USERNAME"),
        "password": os.environ.get("CISCO_PASSWORD"),
        "commands": [
            "show ip interface brief",
            "show version",
        ],
    },
    {
        "name": "linux-server",
        "device_type": "linux",
        "host": os.environ.get("LINUX_HOST"),
        "username": os.environ.get("LINUX_USERNAME"),
        "password": os.environ.get("LINUX_PASSWORD"),
        "commands": [
            "hostname",
            "uptime",
        ],
    },
]

for device in devices:
    print(f"\nConnecting to {device['name']} at {device['host']}...")
    connection = ConnectHandler(
        device_type=device["device_type"],
        host=device["host"],
        username=device["username"],
        password=device["password"],
    )
    for command in device["commands"]:
        output = connection.send_command(command)
        print(f"\n===== {device['name']} :: {command} =====")
        print(output)
    connection.disconnect()
    print(f"Closed {device['name']}")