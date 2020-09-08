# Networking
configuration["asn"] = _config["asn"]

for route in _config["routes"]:
    if ":" in route:
        configuration["ipv6_routes"].append(route)
    else:
        configuration["ipv4_routes"].append(route)


@app.route("/export/bird.conf")
def export_bird_conf():
    with open("automation/bird.j2", "r") as template_file:
        response = make_response(Template(template_file.read()).render(
            asn=configuration["asn"],
            ipv4_routes=configuration["ipv4_routes"],
            ipv6_routes=configuration["ipv6_routes"]
        ), 200)
        response.mimetype = "text/plain"
        return response


@app.route("/export/network.sh")
def export_network_sh():
    with open("config/network.j2", "r") as template_file:
        response = make_response(Template(template_file.read()).render(edge_ips=configuration["edge_ips"]))
        response.mimetype = "text/plain"
        return response