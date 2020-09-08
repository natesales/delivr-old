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
    _config = yaml.safe_load(config_file.read())


# Database
configuration["database"] = _config["database"]

# Authentication
configuration["salt"] = _config["salt"]

# Server
configuration["server_host"] = _config["server-host"]
configuration["server_port"] = _config["server-port"]

configuration["development"] = _config["development"]

# Site Specific
configuration["nameservers"] = _config["nameservers"]
configuration["soa_root"] = _config["soa-root"]
