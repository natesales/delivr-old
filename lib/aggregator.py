from jinja2 import Template


def _build_template(filename, **kwargs) -> str:
    """
    Build and render a template
    :param filename: Path of j2 template file
    :return: Template
    """
    with open(filename, "r") as template_file:
        return Template(template_file.read()).render(kwargs)


zones = {}

for zone in db.get_all_zones():
    zones[zone["zone"]] = _build_template("../config/zone.j2",
                                          serial="mySerial",
                                          records=zone["records"]
                                          )
