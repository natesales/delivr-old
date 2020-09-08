import sys

import requests

try:
    portal_url = sys.argv[1]
except KeyError:
    print("Usage ./assembler.py https://portal.example.com/export")
    exit(1)

zones = requests.get(portal_url).json()

for zone in zones:
    print(zones[zone])
