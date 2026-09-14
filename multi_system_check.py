import os
from netmiko import ConnectHandler

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

print(devices[0]['commands'][0])

for device in devices:
    print(f"\n========== {device['name']} ==========")
    connection = ConnectHandler(**device["connection"])
    for c in device["commands"]:
        print(f"\n----- {device['name']} :: {c} -----")
        print(connection.send_command(c))
    connection.disconnect()
    print(f"Closed {device['name']}")