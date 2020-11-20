#TODO: I'm pretty sure this is how were going to host our app, but I could be jumping the gun so not sure we'll use this
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash #TODO: Not sure all of these are nesessary yet, but well find out

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(32)


app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


#TODO: Populate this with Logic to route to Login Screen or Home Screen depending on if the user is logged into an account
@app.route("/",methods=["GET"])
def root():
    return redirect(url_for("login_get"))


@app.route("/login/",methods=["GET"])
def login_get():
    return render_template("login_signup.html")

@app.route("/login/",methods=["POST"])
def login_post():
    return redirect(url_for("get_user_home"))

@app.route("/signup/",methods=["POST"])
def signup_post():
    session["email"] = request.form.get("signup-email")
    session["password"] = "tempPassword" #TODO: Remove temp password
    return redirect(url_for("signup_info_get"))

@app.route("/signup/",methods=["GET"])
def signup_get():
    return redirect(url_for("login_get"))

@app.route("/signup/info/",methods=["GET"])
def signup_info_get():
    return render_template("user_info_signup.html")

@app.route("/signup/info/",methods=["POST"])
def signup_info_post():
    session["name"] = request.form.get("name")
    session["date-of-birth"] = request.form.get("date-of-birth")
    session["height-feet"] = request.form.get("height-feet")
    session["height-inches"] = request.form.get("height-inches")
    session["weight"] = request.form.get("weight")
    session["gender"] = request.form.get("gender")
    return redirect(url_for("signup_goals_get"))

@app.route("/signup/goals/",methods=["GET"])
def signup_goals_get():
    return render_template("goals_signup.html")

@app.route("/signup/goals/",methods=["POST"])
def signup_goals_post():
    session["weight-goal"] = request.form.get("weight-goal")
    session["excercise-goal"] = request.form.get("excercise-goal")
    return redirect(url_for("get_user_home"))
