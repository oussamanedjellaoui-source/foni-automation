# FONI Automation

## foni_system_validation.py

Validates nine authorized FONI systems over SSH with Netmiko.

The classroom inventory is one Cisco Catalyst 8000V and eight Linux hosts. Validation commands are chosen by operational role.

- router: show ip route (parse_route_output)
- radar-processing: uptime -p (parse_uptime_output)
- monitoring: df -h (parse_disk_output)
- data-ingest: ss -tuln (parse_service_output)
- application: ps aux (parse_process_output)

Every successful Linux system also runs free -h on the same connection. That output is parsed by parse_memory_output.

Connection failures (NetmikoTimeoutException, NetmikoAuthenticationException) print a controlled message and the loop continues.

Credentials come from environment variables. No passwords or enable secrets are stored in source.
