from datetime import timedelta
from os import urandom

from flask import Flask, session, render_template, request, redirect

from lib.aggregator import build_zones
from lib.config import configuration
from lib.database import CDNDatabase

app = Flask(__name__)

if configuration["development"]:
    app.secret_key = b'0'
else:
    app.secret_key = urandom(12)

db = CDNDatabase(configuration["database"], configuration["salt"])


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
                           zones=db.get_zones(session.get("user_id")),
                           total_records=db.get_total_records(session.get("user_id"))
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
            return render_template("errors/400.html", message="Not authorized")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("auth/signup.html")
    elif request.method == "POST":
        error = db.add_user(request.form.get("username"), request.form.get("password"))
        if error is None:
            return redirect("/login")
        else:
            return render_template("errors/400.html", message=error)


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
            return render_template("errors/400.html", message=error)

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
        return render_template("errors/400.html", message="Not authorized for zone")


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
            return render_template("errors/400.html", message=error)

    else:
        return render_template("errors/400.html", message="Unauthorized")

    return redirect("/")


@app.route("/records/<zone>/delete/<record_index>")
def delete_record(zone, record_index):
    if db.authorized_for_zone(session["user_id"], zone):
        db.delete_record(zone, record_index)
        return redirect("/records/" + zone)
    else:
        return redirect("/login")


@app.route("/export/zones")
def export():
    return build_zones(db.get_all_zones())


# @app.route("/api/ddns/<zone>/<domain>")
# def api_ddns(zone, domain):
#     ip = request.headers.get("X-Forwarded-For")
#     auth = request.headers.get("X-API-Token")
#     # todo: auth
#     if zone and ip and domain:
#         db.add_record(zone, domain, "A" if "." in ip else "AAAA", ip, ttl="60")


app.run(
    host=configuration["server-host"],
    port=configuration["server-port"],
    debug=configuration["development"]
)
