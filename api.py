from datetime import timedelta
from os import urandom

from flask import Flask, session

from config import configuration
from database import CDNDatabase

app = Flask(__name__)
app.secret_key = urandom(12)
db = CDNDatabase(configuration.database)


# Set daily rotating sessions
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=1)
