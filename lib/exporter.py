import os
from time import strftime

from jinja2 import Template


def build_zones(zones):
    os.system("rm -rf source/dns/db.*")
    with open("../config/local.j2") as local_template_file:
        local_template = local_template_file.read()

    with open("../config/zone.j2") as zone_template_file:
        zone_template = zone_template_file.read()

    local = ""
    for zone in zones:
        local += Template(local_template).render(zone=zone["zone"])

        with open("source/dns/db." + zone["zone"], "w") as zone_file:
            zone_file.write(Template(zone_template).render(
                zone=zone["zone"],
                records=zone.get("records"),
                serial=strftime("%Y%m%d%S"))
            )

    with open("../source/dns/named.conf.local", "w") as zones_file:
        zones_file.write(local)


def build_nodes(nodes):
    servers = ""
    for server in nodes:
        servers += server["uid"] + " ansible_host=" + server["management"] + "\n"

    with open("automation/hosts", "w") as hosts_file:
        hosts_file.write(servers.strip())
