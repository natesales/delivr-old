from datetime import timedelta
from os import urandom

from flask import Flask, session, render_template, request, redirect

from config import configuration
from database import CDNDatabase

app = Flask(__name__)
app.secret_key = urandom(12)
db = CDNDatabase(configuration["database"])


# Set daily rotating sessions
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=1)


@app.errorhandler(404)
def error_notfound(e):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def error_server(e):
    return render_template("errors/500.html"), 500


@app.route("/")
def index():
    if not session.get("username"):
        return redirect("/login")

    return render_template("index.html",
                           name=session["username"],
                           servers=db.get_nodes(),
                           zones=db.get_zones(session.get("user_id"))
                           )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")
    elif request.method == "POST":
        user_id = db.authenticated(request.form.get("username"), request.form.get("password"))
        if user_id != "":
            session["user_id"] = user_id
            session["username"] = request.form.get("username")
            return redirect("/")
        else:
            return "Not authorized"


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("auth/signup.html")
    elif request.method == "POST":
        error = db.add_user(request.form.get("username"), request.form.get("password"))
        if error is None:
            return redirect("/login")
        else:
            return error


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/new", methods=["GET", "POST"])
def new():
    if not session.get("username"):
        return redirect("/login")

    if request.method == "GET":
        return render_template("new.html",
                               name=session["username"],
                               )

    elif request.method == "POST":
        zone = request.form.get("zone")

        error = db.add_zone(zone, session["user_id"])
        if error:
            return error

        return redirect("/")


@app.route("/records/<zone>", methods=["GET", "POST"])
def records(zone):
    if not session.get("username"):
        return redirect("/login")

    if db.authorized_for_zone(session["user_id"], zone):
        error = db.zone_exists(session["user_id"])
        if error:
            return error

        if request.method == "GET":
            return render_template("records.html",
                                   name=session["username"],
                                   zone=db.get_zone(session["user_id"], zone)
                                   )

        elif request.method == "POST":
            db.add_record(zone, request.form.get("domain"), request.form.get("type"), request.form.get("value"), request.form.get("ttl"))
            return redirect("/records/" + zone)
    else:
        return "Not authorized for zone"


@app.route("/zones")
def zones():
    if not session.get("username"):
        return redirect("/login")

    return render_template("zones.html",
                           name=session["username"],
                           zones=db.get_zones(session.get("user_id"))
                           )


@app.route("/zones/delete/<zone>")
def zone_delete(zone):
    if not session.get("username"):
        return redirect("/login")

    if db.authorized_for_zone(session["user_id"], zone):
        error = db.delete_zone(zone)

        if error:
            return error
    else:
        return "Unauthorized"

    return redirect("/")


@app.route("/records/<zone>/delete/<record_index>")
def delete_record(zone, record_index):
    db.delete_record(zone, record_index)
    return redirect("/records/" + zone)


@app.route("/export")
def export():
    local = ""
    for zone in db.get_all_zones():
        local += "zone \"" + zone["zone"] + "\" {\n  type master;\n  file \"/etc/bind/" + zone["zone"] + "\";\n};\n"

        with open("zone.j2") as zone_template:
            template = Template(zone_template.read()).render(zone=zone["zone"], records=zone.get("records"), serial=time.strftime("%Y%m%d%S"))

            with open("source/dns/" + zone["zone"], "w") as zone_file:
                zone_file.write(template)

    with open("source/dns/zones", "w") as zones_file:
        zones_file.write(local)

    servers = "[nodes]\n"
    for server in db.get_servers():
        if server["status"] == "Operational":
            servers += server["uid"] + " ansible_host=" + server["management"] + "\n"

    with open("hosts", "w") as hosts_file:
        hosts_file.write(servers.strip())

    return "200"


app.run(host="localhost", port=3000, debug=True)
