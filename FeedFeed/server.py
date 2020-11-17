#TODO: I'm pretty sure this is how were going to host our app, but I could be jumping the gun so not sure we'll use this
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash #TODO: Not sure all of these are nesessary yet, but well find out
import sqlite3

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(32)

#TODO: Populate this with Logic to route to Login Screen or Home Screen depending on if the user is logged into an account
@app.route("/")
def root():
    return ""

@app.route("/home/")
def get_user_home():
    conn = sqlite3.connect("Meals.db")
    c = conn.cursor()
    rows = c.execute(''' SELECT * FROM Meals ''')
    info = c.fetchall()
    name = []
    ingredients = []
    image = []
    numItems = len(info)
    for i in range(len(info)):
        name.append(info[i][0])
        ingredients.append(info[i][1])
        image.append(info[i][2])
    return render_template("user_home.html", name=name, ingredients=ingredients, 
                            image=image, numItems=numItems)

@app.route("/mygoals/")
def get_user_goals():
    return render_template("user_goals.html")

@app.route("/mypantry/")
def get_user_pantry():
    return render_template("user_pantry.html")

@app.route("/dailyplan/")
def get_daily_plan():
    return render_template("user_daily_plan.html")