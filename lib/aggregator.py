from jinja2 import Template

from lib.config import configuration


def _build_template(filename, **kwargs) -> str:
    """
    Build and render a template
    :param filename: Path of j2 template file
    :return: Template
    """
    with open(filename, "r") as template_file:
        return Template(template_file.read()).render(kwargs)


def build_zones(db_zones):
    """
    Build zone object
    :param db_zones: Array of zones
    :return:
    """
    zones = {}

    for zone in db_zones:
        zones[zone["zone"]] = _build_template("config/zone.j2",
                                              serial=zone["serial"],
                                              records=zone["records"],
                                              nameservers=configuration["nameservers"],
                                              soa_root=configuration["soa_root"]
                                              )

    return zones

# def export_zones():
#     os.system("rm -rf source/dns/db.*")
#     with open("config/local.j2") as local_template_file:
#         local_template = local_template_file.read()
#
#     with open("config/zone.j2") as zone_template_file:
#         zone_template = zone_template_file.read()
#
#     local = ""
#     for zone in zones:
#         local += Template(local_template).render(zone=zone["zone"])
#
#         with open("source/dns/db." + zone["zone"], "w") as zone_file:
#             zone_file.write(Template(zone_template).render(
#                 zone=zone["zone"],
#                 records=zone.get("records"),
#                 serial=strftime("%Y%m%d%S"))
#             )
#
#     with open("../source/dns/named.conf.local", "w") as zones_file:
#         zones_file.write(local)
