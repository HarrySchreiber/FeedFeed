#TODO: I'm pretty sure this is how were going to host our app, but I could be jumping the gun so not sure we'll use this
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash #TODO: Not sure all of these are nesessary yet, but well find out

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(32)

#TODO: Populate this with Logic to route to Login Screen or Home Screen depending on if the user is logged into an account
@app.route("/")
def root():
    return render_template("login_signup_base.html")