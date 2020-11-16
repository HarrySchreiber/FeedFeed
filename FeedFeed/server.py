#TODO: I'm pretty sure this is how were going to host our app, but I could be jumping the gun so not sure we'll use this
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash #TODO: Not sure all of these are nesessary yet, but well find out

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(32)

#Settings for testing
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

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