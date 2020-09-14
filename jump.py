#!/usr/bin/python3

hosts = {}

with open("hosts", "w") as hosts_file:
    _hosts = hosts_file.read().split("\n")

    for host in _hosts:
        hosts[host] = _hosts[host]

print(hosts)
