import os

import yaml

# All configuration values/types
configuration = {
    "asn": 0,
    "ipv4_routes": [],
    "ipv6_routes": [],
    "database": "",
    "salt": "",
    "server_host": "",
    "server_port": 0,
    "nameservers": []
}

if not os.path.exists("config.yml"):
    print("No config.yml file found.")
    exit(1)

with open("config.yml", "r") as config_file:
    configuration = yaml.safe_load(config_file.read())
