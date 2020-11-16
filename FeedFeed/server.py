#TODO: I'm pretty sure this is how were going to host our app, but I could be jumping the gun so not sure we'll use this
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash #TODO: Not sure all of these are nesessary yet, but well find out
import sqlite3

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(32)

#Settings for testing
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
conn = sqlite3.connect

#TODO: Populate this with Logic to route to Login Screen or Home Screen depending on if the user is logged into an account
@app.route("/")
def root():
    return ""

@app.route("/dash/")
def adminHome():
    #Until we get user logins and db implementation, placeholder data will be used for testing/viewing styling
    return render_template("admin_home.html",
                            username="Administrator",
                            uiSectionName="Home",
                            showBackButton=False)

@app.route("/dash/meals/")
def adminMealManager():
    return render_template("admin_meals.html",
                            username="Administrator",
                            uiSectionName="Home",
                            showBackButton=True,
                            backLink=url_for("adminHome"))

@app.route("/dash/ingredients/")
def adminIngredientManager():
    return render_template("admin_ingredients.html",
                            username="Administrator",
                            uiSectionName="Home",
                            showBackButton=True,
                            backLink=url_for("adminHome"))
@app.route("/home/")
def get_user_home():
    return render_template("user_home.html")

@app.route("/mygoals/")
def get_user_goals():
    return render_template("user_goals.html")

@app.route("/mypantry/")
def get_user_pantry():
    return render_template("user_pantry.html")

@app.route("/dailyplan/")
def get_daily_plan():
    return render_template("user_daily_plan.html")
