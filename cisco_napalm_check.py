"""
Hands-On Activity #7: Use NAPALM with the Cisco Device
Read-only getters only: get_interfaces() and get_facts().
Credentials come from environment variables — never hardcode them.
"""

import os
from pprint import pprint
from napalm import get_network_driver

# Step 4: IOS driver for the FONI Catalyst 8000V (IOS XE)
driver = get_network_driver("ios")

# Step 5: Build the device object from environment variables
# PowerShell (session must already have these set):
#   $env:CISCO_HOST = "54.90.112.247"
#   $env:CISCO_USERNAME = "YOUR_CISCO_USERNAME"
#   $env:CISCO_PASSWORD = "YOUR_CISCO_PASSWORD"
#   $env:CISCO_ENABLE_SECRET = "YOUR_ENABLE_SECRET"
device = driver(
    hostname=os.getenv("CISCO_HOST"),
    username=os.getenv("CISCO_USERNAME"),
    password=os.getenv("CISCO_PASSWORD"),
    optional_args={
        "secret": os.getenv("CISCO_ENABLE_SECRET")
    },
)

# Step 6: Open the connection (NAPALM equivalent of Netmiko ConnectHandler)
device.open()

# Step 7: Structured interface data (not raw "show ip interface brief" text)
interfaces = device.get_interfaces()
print("=== get_interfaces() ===")
pprint(interfaces)

# Step 8: Structured device facts
facts = device.get_facts()
print("\n=== get_facts() ===")
pprint(facts)

# Step 9: One specific interface value — no splitlines() / split() needed
print("\n=== GigabitEthernet1 is_up ===")
print(interfaces["GigabitEthernet1"]["is_up"])

# Step 10: One specific fact, plus one extra key from the facts dict
print("\n=== facts['hostname'] ===")
print(facts["hostname"])

print("\n=== facts['model'] ===")
print(facts["model"])

# Step 11: Always close the session
device.close()
