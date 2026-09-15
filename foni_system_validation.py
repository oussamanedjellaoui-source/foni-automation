"""
Lab #4: Scale FONI Automation Across Nine Systems

One Netmiko program:
  - nine authorized systems
  - role-based validation commands
  - reusable connect / choose / run functions
  - a parser per command type
  - extra free -h memory check on every Linux host
  - specific Netmiko exceptions so one failure does not stop the loop
  - credentials from environment variables only
"""

import os
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException


# ---------------------------------------------------------------------------
# Inventory — authorized FONI systems (IPs are public lab targets, not secrets)
# Table: 1 cisco_ios + 8 linux
# ---------------------------------------------------------------------------
systems = [
    {
        "name": "FONI-Router-01",
        "device_type": "cisco_ios",
        "host": "54.90.112.247",
        "role": "router",
    },
    {
        "name": "FONI-Radar-01",
        "device_type": "linux",
        "host": "3.145.195.223",
        "role": "radar-processing",
    },
    {
        "name": "FONI-Radar-02",
        "device_type": "linux",
        "host": "18.222.205.168",
        "role": "radar-processing",
    },
    {
        "name": "FONI-Monitor-01",
        "device_type": "linux",
        "host": "3.15.204.243",
        "role": "monitoring",
    },
    {
        "name": "FONI-Monitor-02",
        "device_type": "linux",
        "host": "3.140.243.241",
        "role": "monitoring",
    },
    {
        "name": "FONI-Ingest-01",
        "device_type": "linux",
        "host": "18.189.30.63",
        "role": "data-ingest",
    },
    {
        "name": "FONI-Ingest-02",
        "device_type": "linux",
        "host": "3.137.140.116",
        "role": "data-ingest",
    },
    {
        "name": "FONI-Application-02",
        "device_type": "linux",
        "host": "3.14.67.101",
        "role": "application",
    },
    {
        "name": "FONI-Application-01",
        "device_type": "linux",
        "host": "18.117.248.183",
        "role": "application",
    },
]


# ---------------------------------------------------------------------------
# Function #1 — connect
# ---------------------------------------------------------------------------
def connect_to_system(system):
    """Return an open Netmiko connection for one inventory dictionary."""
    device_type = system["device_type"]
    host = system["host"]

    if device_type == "cisco_ios":
        device = {
            "device_type": device_type,
            "host": host,
            "username": os.getenv("CISCO_USERNAME"),
            "password": os.getenv("CISCO_PASSWORD"),
            "secret": os.getenv("CISCO_ENABLE_SECRET"),
            "conn_timeout": 5,
        }
    else:
        device = {
            "device_type": device_type,
            "host": host,
            "username": os.getenv("LINUX_USERNAME"),
            "password": os.getenv("LINUX_PASSWORD"),
            "conn_timeout": 5,
        }

    connection = ConnectHandler(**device)
    if device.get("secret"):
        connection.enable()
    return connection


# ---------------------------------------------------------------------------
# Function #2 — choose command from role
# ---------------------------------------------------------------------------
def choose_command(system):
    """Return the authorized validation command for this system's role."""
    role = system["role"]
    if role == "router":
        return "show ip route"
    elif role == "radar-processing":
        return "uptime -p"
    elif role == "monitoring":
        return "df -h"
    elif role == "data-ingest":
        return "ss -tuln"
    elif role == "application":
        return "ps aux"
    else:
        return None


# ---------------------------------------------------------------------------
# Function #3 — run command
# ---------------------------------------------------------------------------
def run_command(connection, command):
    """Execute command on an open connection and return raw output."""
    return connection.send_command(command)


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------
def parse_uptime_output(output):
    """Clean uptime -p text."""
    return output.strip()


def parse_disk_output(output):
    """Extract size/used/avail/use% for the root filesystem."""
    for line in output.splitlines()[1:]:
        fields = line.split()
        if len(fields) >= 6 and fields[-1] == "/":
            return {
                "Size": fields[1],
                "Used": fields[2],
                "Available": fields[3],
                "Usage": fields[4],
            }
    return None


def parse_service_output(output):
    """Count listening TCP and UDP sockets from ss -tuln."""
    tcp = 0
    udp = 0
    for line in output.splitlines()[1:]:
        fields = line.split()
        if not fields:
            continue
        proto = fields[0].lower()
        if proto.startswith("tcp"):
            tcp += 1
        elif proto.startswith("udp"):
            udp += 1
    return {"tcp": tcp, "udp": udp}


def parse_process_output(output):
    """Count process rows from ps aux, excluding the heading."""
    count = 0
    for line in output.splitlines()[1:]:
        if line.strip():
            count += 1
    return count


def parse_route_output(output):
    """Gateway of last resort plus a count of observed route-entry lines."""
    gateway = None
    route_count = 0
    route_prefixes = ("C", "L", "S", "O", "D", "B", "R", "i", "IA", "E1", "E2", "N1", "N2")

    for line in output.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if "Gateway of last resort" in stripped:
            gateway = stripped
            continue
        first = stripped.split()[0]
        # Codes may be like "C", "S*", "O E2", "L"
        if first.rstrip("*") in route_prefixes or first.startswith(route_prefixes):
            # Skip the codes-legend lines that only define letters
            if " - " in stripped and stripped.startswith(first) and len(stripped.split()) > 4:
                # legend lines look like "C - connected, ..."
                if " - " in stripped[:20]:
                    continue
            if stripped.startswith(tuple(p + " - " for p in "CLSODBRi")):
                continue
            route_count += 1

    return {"gateway": gateway, "route_count": route_count}


def parse_memory_output(output):
    """Extract total / used / available from the Mem: line of free -h."""
    for line in output.splitlines():
        stripped = line.strip()
        if stripped.startswith("Mem:"):
            fields = stripped.split()
            # free -h: Mem: total used free shared buff/cache available
            result = {"total": None, "used": None, "available": None}
            if len(fields) >= 3:
                result["total"] = fields[1]
                result["used"] = fields[2]
            if len(fields) >= 7:
                result["available"] = fields[6]
            elif len(fields) >= 4:
                result["available"] = fields[3]
            return result
    return None


def display_parsed_result(role, parsed):
    """Print the Commander-facing summary for one role."""
    if role == "router":
        if parsed["gateway"]:
            print(parsed["gateway"])
        else:
            print("Gateway of last resort: not found")
        print(f"Route entries identified: {parsed['route_count']}")
    elif role == "radar-processing":
        print(f"Uptime: {parsed}")
    elif role == "monitoring":
        if parsed:
            print(f"Size: {parsed['Size']}")
            print(f"Used: {parsed['Used']}")
            print(f"Available: {parsed['Available']}")
            print(f"Usage: {parsed['Usage']}")
        else:
            print("Root filesystem (/) not found in df -h output.")
    elif role == "data-ingest":
        print(f"Listening TCP sockets: {parsed['tcp']}")
        print(f"Listening UDP sockets: {parsed['udp']}")
    elif role == "application":
        print(f"Running processes identified: {parsed}")


def parse_by_role(role, output):
    if role == "router":
        return parse_route_output(output)
    if role == "radar-processing":
        return parse_uptime_output(output)
    if role == "monitoring":
        return parse_disk_output(output)
    if role == "data-ingest":
        return parse_service_output(output)
    if role == "application":
        return parse_process_output(output)
    return None


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------
def validate_system(system):
    name = system["name"]
    role = system["role"]
    command = choose_command(system)

    print("=" * 64)
    print(f"System: {name}")
    print(f"Role:   {role}")
    print(f"Command: {command}")
    print("=" * 64)

    connection = None
    try:
        connection = connect_to_system(system)
        raw = run_command(connection, command)
        parsed = parse_by_role(role, raw)
        print("\nParsed result:")
        display_parsed_result(role, parsed)

        if system["device_type"] == "linux":
            memory_raw = run_command(connection, "free -h")
            memory = parse_memory_output(memory_raw)
            print("\nMemory (free -h):")
            if memory:
                print(f"Total memory: {memory['total']}")
                print(f"Used memory: {memory['used']}")
                print(f"Available memory: {memory['available']}")
            else:
                print("Mem: line not found in free -h output.")

        print(f"\n[OK] {name}")

    except NetmikoTimeoutException:
        print(f"FAILED: CONNECTION TIMEOUT  ({name})")

    except NetmikoAuthenticationException:
        print(f"FAILED: AUTHENTICATION NOT ACCEPTED  ({name})")

    finally:
        if connection:
            connection.disconnect()


def main():
    print(f"FONI validation — {len(systems)} authorized systems\n")
    for system in systems:
        validate_system(system)
        print()
    print("All nine systems attempted.")


if __name__ == "__main__":
    main()
