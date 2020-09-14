import os

import yaml

if not os.path.exists("config.yml"):
    print("No config.yml file found.")
    exit(1)

with open("config.yml", "r") as config_file:
    configuration = yaml.safe_load(config_file.read())

configuration["ipv4_routes"] = ""
configuration["ipv6_routes"] = ""
for route in configuration["routes"]:
    if ":" in route:
        configuration["ipv6_routes"] += route + ","
    else:
        configuration["ipv4_routes"] += route + ","

configuration["ipv4_routes"] = configuration["ipv4_routes"][:-1]
configuration["ipv6_routes"] = configuration["ipv6_routes"][:-1]
