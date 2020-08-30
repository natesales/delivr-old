from jinja2 import Template
from time import strftime

def build_zone(zone, records):
local += "zone \"" + zone["zone"] + "\" {\n  type master;\n  file \"/etc/bind/" + zone["zone"] + "\";\n};\n"

        with open("zone.j2") as zone_template:
            template = Template(zone_template.read()).render(zone=zone["zone"], records=zone.get("records"), serial=time.strftime("%Y%m%d%S"))

            with open("source/dns/" + zone["zone"], "w") as zone_file:
                zone_file.write(template)

    with open("source/dns/zones", "w") as zones_file:
        zones_file.write(local)

