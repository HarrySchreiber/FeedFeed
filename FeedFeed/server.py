#TODO: I'm pretty sure this is how were going to host our app, but I could be jumping the gun so not sure we'll use this
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, g, abort #TODO: Not sure all of these are nesessary yet, but well find out
import sqlite3
import base64
import re
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from passlib.hash import argon2

serverdir = os.path.dirname(__file__)
pepfile = os.path.join(serverdir,"pepper.bin")
with open(pepfile, 'rb') as fin:
    key = fin.read()
    pep = Fernet(key)


from passlib.hash import bcrypt_sha256

from feedFeedData import Ingredient, Meal, unitOpts, MealIng

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(32)

#Settings for testing
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
conn = sqlite3.connect

#Database connection
DATABASE = 'Database.db'

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def hash_password(pwd,pep):
    h = argon2.using(rounds=10).hash(pwd)
    ph = pep.encrypt(h.encode('utf-8'))
    b64ph = base64.b64encode(ph)
    return b64ph

def check_password(pwd, b64ph, pep):
    ph = base64.b64decode(b64ph)
    h = pep.decrypt(ph)
    return argon2.verify(pwd,h)

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

#Routes
@app.route("/",methods=["GET"])
def root():
    #TODO: Set this admin flag forreal
    admin_flag = False
    if(admin_flag):
        return redirect(url_for("adminHome"))
    if(session.get("uid") is not None):
        return redirect(url_for("get_user_home"))
    return redirect(url_for("login_get"))

@app.route("/", methods=["POST"])
def post_root():
    session['uid'] = None
    session['expires'] = ""
    return redirect(url_for("login_get"))


@app.route("/login/",methods=["GET"])
def login_get():
    return render_template("login_signup.html")

@app.route("/login/",methods=["POST"])
def login_post():
    if request.form.get("login-email") is None or request.form.get("login-email")=="":
        flash("Must have an Email")
        return redirect(url_for("login_get"))
    if request.form.get("login-password") is None or request.form.get("login-password")=="":
        flash("Must have a Password")
        return redirect(url_for("login_get"))
    
    if re.search('^[a-zA-Z0-9\.]+[\._]?[a-zA-Z0-9]+[@]\w+[.]\w{2,3}$',request.form.get("login-email")) is None:
        flash("Malformed Email Address")
        return redirect(url_for("login_get"))
    
    if len(request.form.get("login-password")) < 8:
        flash("Password must be at least 8 characters")
        return redirect(url_for("login_get"))

    c = get_db().cursor()
    user = c.execute("""
        SELECT id, password FROM User WHERE email=?;
    """,(request.form.get("login-email").lower(),)).fetchone()

    if user is not None and check_password(request.form.get("login-password"),user[1],pep):
        expires = datetime.utcnow()+timedelta(hours=24)
        session["uid"] = user[0]
        session["expires"] = expires.strftime("%Y-%m-%dT%H:%M:%SZ")
        return redirect(url_for("get_user_home"))
    
    flash("Username or Password does not match")
    return redirect(url_for("login_get"))

@app.route("/signup/",methods=["POST"])
def signup_post():
    if request.form.get("signup-email") is None or request.form.get("signup-email")=="":
        flash("Must have an Email")
        return redirect(url_for("signup_get"))
    if request.form.get("signup-password") is None or request.form.get("signup-password")=="":
        flash("Must have a Password")
        return redirect(url_for("signup_get"))
    if request.form.get("signup-confirm-password") is None or request.form.get("signup-confirm-password")=="":
        flash("Must confirm your password")
        return redirect(url_for("signup_get"))

    
    if re.search('^[a-zA-Z0-9\.]+[\._]?[a-zA-Z0-9]+[@]\w+[.]\w{2,3}$',request.form.get("signup-email")) is None:
        flash("Malformed Email Address")
        return redirect(url_for("signup_get"))

    if len(request.form.get("signup-password")) < 8:
        flash("Password must be at least 8 characters")
        return redirect(url_for("signup_get"))
    if len(request.form.get("signup-confirm-password")) < 8:
        flash("Password must be at least 8 characters")
        return redirect(url_for("signup_get"))

    c = get_db().cursor()
    uid = c.execute("""
        SELECT id FROM User WHERE email=?;
    """,(request.form.get("signup-email").lower(),)).fetchone()
    if uid is not None:
        flash("An account with this email address already exists")
        return redirect(url_for("signup_get"))

    h = hash_password(request.form.get("signup-password"),pep)

    if(not check_password(request.form.get("signup-confirm-password"),h,pep)):
        flash("Passwords must match")
        return redirect(url_for("signup_get"))

    session["email"] = request.form.get("signup-email").lower()
    session["password"] = h
    return redirect(url_for("signup_info_get"))

@app.route("/signup/",methods=["GET"])
def signup_get():
    return redirect(url_for("login_get"))

@app.route("/signup/info/",methods=["GET"])
def signup_info_get():
    if(session.get("email") is None or session.get("password") is None):
        flash("Please follow the signup process procedurally")
        return redirect(url_for("login_get"))
    return render_template("user_info_signup.html")

@app.route("/signup/info/",methods=["POST"])
def signup_info_post():
    if request.form.get("name") is None or request.form.get("name")=="":
        flash("Must have a Name")
        return redirect(url_for("signup_info_get"))
    if request.form.get("date-of-birth") is None or request.form.get("date-of-birth")=="":
        flash("Must have an Date of Birth")
        return redirect(url_for("signup_info_get"))
    if datetime.strptime(request.form.get("date-of-birth"), '%Y-%m-%d').date()>=datetime.today().date():
        flash("Date must be before today")
        return redirect(url_for("signup_info_get"))
    if request.form.get("height-feet") is None or request.form.get("height-feet")=="":
        flash("Must provide height in feet")
        return redirect(url_for("signup_info_get"))
    if request.form.get("height-inches") is None or request.form.get("height-inches")=="":
        flash("Must provide height in inches")
        return redirect(url_for("signup_info_get"))
    if not request.form.get("height-feet").isnumeric():
        flash("Height in feet must be a number")
        return redirect(url_for("signup_info_get"))
    if not request.form.get("height-inches").isnumeric():
        flash("Height in inches must be a number")
        return redirect(url_for("signup_info_get"))
    if int(request.form.get("height-feet")) < 1 or int(request.form.get("height-feet")) > 10:
        flash("Height must be between 1 and 10 feet")
        return redirect(url_for("signup_info_get"))
    if int(request.form.get("height-inches")) < 0 or int(request.form.get("height-inches")) > 12:
        flash("Height in inches must be between 0 and 12 inches")
        return redirect(url_for("signup_info_get"))
    if request.form.get("weight") is None or request.form.get("weight")=="":
        flash("Must provide weight in pounds")
        return redirect(url_for("signup_info_get"))
    if int(request.form.get("weight")) <= 0 or int(request.form.get("weight")) > 1500:
        flash("Weight must be between 1 pound and 1500 pounds")
        return redirect(url_for("signup_info_get"))
    if request.form.get("gender") is None or request.form.get("gender")=="":
        flash("Must provide a gender")
        return redirect(url_for("signup_info_get"))
    if request.form.get("gender") != "male" and request.form.get("gender")!="female":
        flash("Gender must be Male or Female")
        return redirect(url_for("signup_info_get"))

    session["name"] = request.form.get("name")
    session["date-of-birth"] = request.form.get("date-of-birth")
    session["height-feet"] = request.form.get("height-feet")
    session["height-inches"] = request.form.get("height-inches")
    session["weight"] = request.form.get("weight")
    session["gender"] = request.form.get("gender")
    return redirect(url_for("signup_goals_get"))

@app.route("/signup/goals/",methods=["GET"])
def signup_goals_get():
    if(session.get("name") is None or session.get("date-of-birth") is None or session.get("height-feet") is None or session.get("height-inches") is None or session.get("weight") is None or session.get("gender") is None):
        flash("Please follow the signup process procedurally")
        return redirect(url_for("login_get"))
    return render_template("goals_signup.html")

@app.route("/signup/goals/",methods=["POST"])
def signup_goals_post():
    
    if request.form.get("weight-goal") is None or request.form.get("weight-goal")=="":
        flash("Must provide a weight goal")
        return redirect(url_for("signup_goals_get"))
    print(request.form.get("weight-goal"))
    if request.form.get("weight-goal") != "cut" and request.form.get("weight-goal") != "maintain" and request.form.get("weight-goal") != "bulk":
        flash("Weight Goal must be either cut, maintain, or bulk")
        return redirect(url_for("signup_goals_get"))
    if request.form.get("exercise-goal") is None or request.form.get("exercise-goal")=="":
        flash("Must provide an exercise goal")
        return redirect(url_for("signup_goals_get"))
    if request.form.get("exercise-goal") != "1.2" and request.form.get("exercise-goal") != "1.375" and request.form.get("exercise-goal") != "1.55" and request.form.get("exercise-goal") != "1.725" and request.form.get("exercise-goal") != "1.9":
        flash("Exercise Goal must have a valid value")
        return redirect(url_for("signup_goals_get"))

    session["weight-goal"] = request.form.get("weight-goal")
    session["exercise-goal"] = request.form.get("exercise-goal")


    if session.get("email") is None or session.get("password") is None or session.get("name") is None or session.get("date-of-birth") is None or session.get("height-feet") is None or session.get("height-inches") is None or session.get("weight") is None or session.get("gender") is None or session.get("weight-goal") is None or session.get("exercise-goal") is None:
        flash("Something went wrong during signup, make sure to follow through signup sequentially")
        return redirect(url_for("signup_get"))
    c = get_db().cursor()
    c.execute("""
        INSERT INTO User (email,password,name,dob,height_feet,height_inches,weight,gender,weight_goal,exercise_goal)
        VALUES (?,?,?,?,?,?,?,?,?,?);
    """,(session.get("email"),session.get("password"),session.get("name"),session.get("date-of-birth"),session.get("height-feet"),session.get("height-inches"),session.get("weight"),session.get("gender"),session.get("weight-goal"),session.get("exercise-goal")))
    get_db().commit()

    user = c.execute("""
        SELECT id FROM User WHERE email=?;
    """,(session.get("email").lower(),)).fetchone()

    if user is not None:
        expires = datetime.utcnow()+timedelta(hours=24)
        session["uid"] = user[0]
        session["expires"] = expires.strftime("%Y-%m-%dT%H:%M:%SZ")
        return redirect(url_for("get_user_home"))
    
    flash("Something Went Wrong")
    return redirect(url_for("signup_goals_get"))

    

@app.route("/dash/")
def adminHome():
    #TODO: Set this admin flag forreal
    admin_flag = True
    if(not admin_flag):
        flash("Restricted Access")
        return redirect(url_for("login_get"))
    #Until we get user logins and db implementation, placeholder data will be used for testing/viewing styling
    return render_template("admin_home.html",
                            username="Administrator",
                            uiSectionName="Home",
                            showBackButton=False)

@app.route("/dash/meals/")
def adminMealManager():
    #TODO: Set this admin flag forreal
    admin_flag = True
    if(not admin_flag):
        flash("Restricted Access")
        return redirect(url_for("login_get"))
    mealData = dict()

    c = get_db().cursor()

    t = c.execute("""
        SELECT id, name, description, image, serves, calories_per_serving FROM Meal;
    """).fetchall()

    for record in t:
        mealData[record[0]] = Meal(record[0], record[1], record[2], record[3], record[4], record[5], None)

    return render_template("admin_meals.html",
                            username="Administrator",
                            uiSectionName="Meals",
                            showBackButton=True,
                            backLink=url_for("adminHome"),
                            tableData = mealData)

@app.route("/dash/meals/edit/", methods=["GET"])
def adminEditMeal():
    #TODO: Set this admin flag forreal
    admin_flag = True
    if(not admin_flag):
        flash("Restricted Access")
        return redirect(url_for("login_get"))
    ingData = dict()

    args = request.args

    c = get_db().cursor()

    #If an action was specified and valid, use that. Otherwise, "New"
    if "action" in args:
        if args["action"] == "New" or args["action"] == "Edit":
            action = args["action"]
    else:
        action = "New"

    t = c.execute("""
        SELECT id, name, calories, protein, carbs, fat FROM Ingredient;
    """).fetchall()

    for record in t:
        ingData[record[0]] = Ingredient(record[0], record[1], record[2], record[3], record[4], record[5], False)

    if action == "New":
        return render_template("admin_edit_meal.html",
                                username="Administrator",
                                uiSectionName=f"{action} Meal",
                                showBackButton=True,
                                backLink=url_for("adminMealManager"),
                                action=action,
                                unitOpts = unitOpts,
                                ingredientOpts=ingData)
    elif action == "Edit":
        if "id" in args:
            try:
                mealId = int(args["id"])
            except:
                abort(404)

            #Check id exists
            idCnt = c.execute("""
                SELECT COUNT(*) FROM Meal WHERE id == ?
            """, (mealId,)).fetchone()

            if(idCnt[0] == 0):
                abort(404)

            mealIngs = list()
            #Fetch ingredient information
            c = get_db().cursor()

            ingInfo = c.execute("""
                SELECT ingredient_id, name, quantity, unit FROM Ingredient
                JOIN
                (SELECT ingredient_id, quantity, unit FROM MealIngredients WHERE meal_id == ?) AS MealRel
                ON
                Ingredient.id == MealRel.ingredient_id;
            """, (mealId,)).fetchall()

            for ing in ingInfo:
                mealIngs.append(MealIng(ing[0], ing[1], ing[2], ing[3]))

            mealInfo = c.execute("""
                SELECT id, name, description, image, serves, calories_per_serving FROM Meal WHERE id == ?
            """, (mealId,)).fetchone()

            currentMeal = Meal(mealInfo[0], mealInfo[1], mealInfo[2], mealInfo[3], mealInfo[4], mealInfo[5], mealIngs)

            print(currentMeal.ingredients)

            return render_template("admin_edit_meal.html",
                                    username="Administrator",
                                    uiSectionName=f"{action} Ingredient",
                                    meal=currentMeal,
                                    showBackButton=True,
                                    backLink=url_for("adminMealManager"),
                                    action=action,
                                    unitOpts = unitOpts,
                                    ingredientOpts=ingData)
    
    abort(404)

@app.route("/dash/meals/edit/", methods=["POST"])
def adminEditMealPost():
    #TODO: Set this admin flag forreal
    admin_flag = True
    if(not admin_flag):
        flash("Restricted Access")
        return redirect(url_for("login_get"))
    #Get db cursor
    c = get_db().cursor()

    mealData = dict()
    ingData = dict()
    mealId = 0 #Init to bogus value

    #Validation
    fields = ["id", "mealName", "description", "mealServes", "caloriesPer", "imageUrl"]
    lists = ["quantity", "units", "ingredients"]
    requiredFields = ["id", "mealName", "mealServes", "caloriesPer", "imageUrl"]

    for field in fields:
        mealData[field] = request.form.get(field)

    for l in lists:
        ingData[l] = request.form.getlist(l)
    
    #Server side validation
    valid = True

    #Check required fields
    for field in requiredFields:
        if mealData[field] is None or mealData[field] == "":
            flash(f"{field} is required")
            valid = False

    if valid and len(ingData["ingredients"]) == 0:
        flash("At least one ingredient is required")
        valid = False

    #Check that meal id is an int
    if valid:
        try:
            mealId = int(mealData["id"])
        except:
            flash("Invalid meal id provided")
            valid = False

    #Check that meal id (for edit) exists
    if valid and mealId != -1:
        idCnt = c.execute("""
            SELECT COUNT(*) FROM Meal WHERE id == ?
        """, (mealId,)).fetchone()
        if idCnt[0] != 1:
            flash("Invalid meal id provided")
            valid = False

    #Check numbers
    if valid:
        try:
            int(mealData["mealServes"])
        except:
            flash("Number serves must be an integer")
            valid = False

    if valid:
        try:
            float(mealData["caloriesPer"])
        except:
            flash("Calories per serving must be a float")
            valid = False

    if valid:
        valIng = list()
        #Check for duplicate ingredients
        for ingredient in ingData["ingredients"]:
            if ingredient in valIng:
                flash("Two of the same ingredient submitted")
                valid = False
            else:
                valIng.append(ingredient)

    if valid:
        #Check quantity numbers
        for quantity in ingData["quantity"]:
            try:
                qnt = float(quantity)
                if qnt <= 0:
                    flash("All quantities must be greater than zero")
                    valid = False
            except:
                flash("All quantities must be floating point numbers")
                valid = False
    if valid:
        #Check units
        for unit in ingData["units"]:
            if unit not in unitOpts:
                flash(f"{unit} is not a valid unit")
                valid = False


    if not valid:
        return redirect(url_for("adminEditMeal"))

    #Add the meal data to database
    if mealId == -1:
        #get max id
        maxId = c.execute("""
            SELECT MAX(id) FROM Meal
        """).fetchone()

        try:
            newId = int(maxId[0]) + 1
        except:
            newId = 0

        mealId = newId

        if mealData["description"] is not None and mealData["description"] != "":
            c.execute("""
                INSERT INTO Meal (id, name, image, description, serves, calories_per_serving)
                VALUES (?, ?, ?, ?, ?, ?);
            """, (newId, mealData["mealName"], mealData["imageUrl"], mealData["description"], mealData["mealServes"], mealData["caloriesPer"]))
        else:
            c.execute("""
                INSERT INTO Meal (id, name, image, serves, calories_per_serving)
                VALUES (?, ?, ?, ?, ?, ?);
            """, (newId, mealData["mealName"], mealData["imageUrl"], mealData["mealServes"], mealData["caloriesPer"]))

        get_db().commit()
    
    else:
        #Update meal data
        c.execute("""
            UPDATE Meal
            SET image = ?, description = ?, serves = ?, calories_per_serving = ?
            WHERE id == ?
        """, (mealData["imageUrl"], mealData["description"], mealData["mealServes"], mealData["caloriesPer"], mealId))

        #Remove old ingredients
        c.execute("""
            DELETE FROM MealIngredients WHERE meal_id == ?
        """, (mealId,))

    #Add the ingredient data to database
    for i in range(len(ingData["ingredients"])):
        c.execute("""
            INSERT INTO MealIngredients (meal_id, ingredient_id, quantity, unit)
            VALUES (?, ?, ?, ?)
        """, (mealId, ingData["ingredients"][i], ingData["quantity"][i], ingData["units"][i]))
    
    get_db().commit()
    
    return redirect(url_for("adminMealManager"))

#Displays all the ingredients in the database in a readable format and provides management options
@app.route("/dash/ingredients/")
def adminIngredientManager():
    #TODO: Set this admin flag forreal
    admin_flag = True
    if(not admin_flag):
        flash("Restricted Access")
        return redirect(url_for("login_get"))
    ingData = dict()

    c = get_db().cursor()

    t = c.execute("""
        SELECT id, name, calories, protein, carbs, fat FROM Ingredient;
    """).fetchall()

    for record in t:
        ingData[record[0]] = Ingredient(record[0], record[1], record[2], record[3], record[4], record[5], False)

    return render_template("admin_ingredients.html",
                            username="Administrator",
                            uiSectionName="Ingredients",
                            showBackButton=True,
                            backLink=url_for("adminHome"),
                            tableData = ingData)

@app.route("/dash/ingredients/edit/", methods=["GET"])
def adminEditIngredient():
    #TODO: Set this admin flag forreal
    admin_flag = True
    if(not admin_flag):
        flash("Restricted Access")
        return redirect(url_for("login_get"))
    args = request.args

    #If an action was specified and valid, use that. Otherwise, "New"
    if "action" in args:
        if args["action"] == "New" or args["action"] == "Edit":
            action = args["action"]
    else:
        action = "New"

    if action == "New":
        return render_template("admin_edit_ingredient.html",
                                username="Administrator",
                                uiSectionName=f"{action} Ingredient",
                                showBackButton=True,
                                backLink=url_for("adminIngredientManager"),
                                action=action)
    elif action == "Edit":
        if "id" in args:
            try:
                ingId = int(args["id"])
            except:
                abort(404)

            #Fetch ingredient information
            c = get_db().cursor()

            ingInfo = c.execute("""
                SELECT id, name, calories, protein, carbs, fat, is_meal FROM Ingredient WHERE id == ?
            """, (ingId,)).fetchone()

            currentIngredient = Ingredient(ingInfo[0], ingInfo[1], ingInfo[2], ingInfo[3], ingInfo[4], ingInfo[5], ingInfo[6] == 1)

            return render_template("admin_edit_ingredient.html",
                                    username="Administrator",
                                    uiSectionName=f"{action} Ingredient",
                                    ingredient=currentIngredient,
                                    showBackButton=True,
                                    backLink=url_for("adminIngredientManager"),
                                    action=action)
    
    abort(404)

@app.route("/dash/ingredients/edit/", methods=["POST"])
def adminEditIngredientPost():
    #TODO: Set this admin flag forreal
    admin_flag = True
    if(not admin_flag):
        flash("Restricted Access")
        return redirect(url_for("login_get"))
    #Get db cursor
    c = get_db().cursor()

    #Validation
    data = dict()
    fields = ["id", "ingName", "isMeal", "calories", "protein", "carbs", "fat"]
    numFields = ["calories", "protein", "carbs", "fat"]
    ingId = 0 #Init with bogus id

    for field in fields:
        data[field] = request.form.get(field)

    valid = True
    for field in fields:
        if field != "isMeal" and (data[field] is None or data[field] == ""):
            valid = False
            flash(f"{field} cannot be blank")
    
    #Check numbers
    if valid:
        for field in numFields:
            try:
                if float(data[field]) < 0:
                    valid = False
                    flash(f"{field} cannot be less than zero")
            except:
                valid = False
                flash(f"{field} must be a float")

    #Check results against database (neg id means adding new)
    if valid:    
        try:
            ingId = int(data["id"])

            if ingId > 0:
                #Check id
                cnt = c.execute("""
                    SELECT COUNT(*) FROM Ingredient WHERE id == ?
                """, (ingId,)).fetchone()
                if int(cnt[0]) != 1:
                    valid = False
                    flash("Attempting to edit ingredient that doesn't exist")
                else:
                    #Check name
                    currentName = c.execute("""
                        SELECT name FROM Ingredient WHERE id == ?
                    """, (ingId,)).fetchone()
                    if data["ingName"] != currentName[0]:
                        valid = False
                        flash("Cannot change name of existing ingredient")
            elif ingId == -1:
                cntName = c.execute("""
                    SELECT COUNT(*) FROM Ingredient WHERE name = ?
                """, (data["ingName"],)).fetchone()

                if int(cntName[0]) != 0:
                    valid = False
                    flash(f"Ingredient \"{data['ingName']}\" already exists, please edit existing ingredient or choose a different name")
                    redirect(url_for("adminEditIngredient"))
            else:
                valid = False
                flash("Invalid id value supplied")
        except:
            valid = False
            flash("Invalid id value supplied")
    
    if not valid:
        redirect(url_for("adminEditIngredient"))

    #Now that the input is validated, lets add it to the db
    #Clean up isMeal
    if data["isMeal"] is None:
        isMealVal = 0
    else:
        isMealVal = 1
    
    if ingId == -1:
        #get max id
        maxId = c.execute("""
            SELECT MAX(id) FROM Ingredient
        """).fetchone()

        newId = int(maxId[0]) + 1

        c.execute("""
            INSERT INTO Ingredient (id, calories, protein, carbs, fat, is_meal, name)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (newId, data["calories"], data["protein"], data["carbs"], data["fat"], isMealVal, data["ingName"]))

        get_db().commit()

        if isMealVal == 1:
            #get max id
            maxMealId = c.execute("""
                SELECT MAX(id) FROM Meal
            """).fetchone()

            try:
                mealId = int(maxMealId[0]) + 1
            except:
                mealId = 0

            c.execute("""
                INSERT INTO Meal (id, name, image, serves, calories_per_serving)
                VALUES (?, ?, ?, ?, ?)
            """, (mealId, data["ingName"], "/static/images/default_ingredient_meal.png", 1, data["calories"]))

            get_db().commit()

            c.execute("""
                INSERT INTO MealIngredients (meal_id, ingredient_id, quantity, unit)
                VALUES (?, ?, ?, ?)
            """, (mealId, newId, 1, "oz"))

    elif ingId > 0:
        c.execute("""
           UPDATE Ingredient
           SET calories = ?, protein = ?, carbs = ?, fat = ?
           WHERE id == ?
        """, (data["calories"], data["protein"], data["carbs"], data["fat"], data["id"]))

    get_db().commit()

    return redirect(url_for("adminIngredientManager"))

@app.route("/dash/ingredients/remove/", methods=["POST"])
def adminRemoveIngredientPost():
    #TODO: Set this admin flag forreal
    admin_flag = True
    if(not admin_flag):
        flash("Restricted Access")
        return redirect(url_for("login_get"))
    c = get_db().cursor()

    ingId = request.get_json()["itemId"]

    mealIds = c.execute("""
        SELECT meal_id FROM MealIngredients WHERE ingredient_id == ?
    """, (ingId,)).fetchall()

    for mealId in mealIds:
        c.execute("""
        DELETE FROM MealIngredients WHERE meal_id == ?
        """, (mealId[0],))

        get_db().commit()

        c.execute("""
            DELETE FROM Meal WHERE id == ?
        """, (mealId[0],))

        get_db().commit()

    c.execute("""
        DELETE FROM Ingredient WHERE id == ?
    """, (ingId,))

    get_db().commit()

    return "Ingredient removed"

@app.route("/dash/meals/remove/", methods=["POST"])
def adminRemoveMealPost():
    #TODO: Set this admin flag forreal
    admin_flag = True
    if(not admin_flag):
        flash("Restricted Access")
        return redirect(url_for("login_get"))
    c = get_db().cursor()

    mealId = request.get_json()["itemId"]

    c.execute("""
        DELETE FROM MealIngredients WHERE meal_id == ?
    """, (mealId,))

    get_db().commit()

    c.execute("""
        DELETE FROM Meal WHERE id == ?
    """, (mealId,))

    get_db().commit()

    return "Meal romoved"

@app.route("/home/")
def get_user_home():
    if(session.get("uid") is None):
        flash("Must Sign Into an Account")
        return redirect(url_for("login_get"))
    conn = sqlite3.connect("Database.db")
    c = conn.cursor()
    rows = c.execute(''' SELECT * FROM Meal; ''')

    conn2 = sqlite3.connect("Database.db")
    c2 = conn.cursor()
    mealIngs = c2.execute(''' 
    SELECT * FROM MealIngredients JOIN Ingredient ON MealIngredients.ingredient_id = Ingredient.id
     JOIN Meal ON Meal.id = MealIngredients.meal_id;
     ''').fetchall()
    return render_template("user_home.html", rows=rows, mealIngs=mealIngs)

@app.route("/mygoals/")
def get_user_goals():
    if(session.get("uid") is None):
        flash("Must Sign Into an Account")
        return redirect(url_for("login_get"))
    conn = sqlite3.connect("Database.db")
    c = conn.cursor()
    rows = c.execute(''' SELECT * FROM User WHERE id = ?; ''', (session['uid'],))
    for entry in rows:
        name = entry[3]
        dob = entry[4]
        heightFeet = entry[5]
        heightInches = entry[6]
        weight = entry[7]
        weightGoal = entry[9]
        exerciseGoal = entry[10]
    print(exerciseGoal)
    return render_template(
        "user_goals.html", 
        name=name, 
        dob=dob,
        heightFeet=heightFeet, 
        heightInches=heightInches, 
        weight=weight, 
        weightGoal=weightGoal, 
        exerciseGoal=exerciseGoal
    )

@app.route("/mygoals/save/", methods=["POST"])
def save_goals():
    result = request.get_json()
    conn = sqlite3.connect("Database.db")
    c = conn.cursor()

    if 'height_feet' in result and result["height_feet"] is not None and result["height_feet"] != "":
        c.execute("UPDATE User SET height_feet = ? WHERE id = ?; ", (result["height_feet"], session['uid']))
    if 'height_inches' in result and result["height_inches"] is not None and result["height_inches"] != "":
        c.execute("UPDATE User SET height_inches = ? WHERE id = ?; ", (result["height_inches"], session['uid']))
    if 'weight' in result and result["weight"] is not None and result["weight"] != "":
        c.execute("UPDATE User SET weight = ? WHERE id = ?; ", (result["weight"], session['uid']))
    if 'weight_goal' in result and result["weight_goal"] is not None and result["weight_goal"] != "":
        c.execute("UPDATE User SET weight_goal = ? WHERE id = ?; ", (result["weight_goal"], session['uid']))
    if 'exercise_goal' in result and result["exercise_goal"] is not None and result["exercise_goal"] != "":
        c.execute("UPDATE User SET exercise_goal = ? WHERE id = ?; ", (result["exercise_goal"], session['uid']))
    conn.commit()
    return render_template("user_goals.html")

@app.route("/mypantry/")
def get_user_pantry():
    if(session.get("uid") is None):
        flash("Must Sign Into an Account")
        return redirect(url_for("login_get"))
    conn = sqlite3.connect("Database.db")
    c = conn.cursor()
    rows = c.execute(''' SELECT * FROM Ingredient ''')

    conn2 = sqlite3.connect("Database.db")
    s = conn2.cursor()
    ingredients = s.execute(''' SELECT DISTINCT name FROM Ingredient JOIN UserIngredients
                            ON UserIngredients.ingredient=Ingredient.id WHERE UserIngredients.user=?;''', (session['uid'],)).fetchall()
    return render_template("user_pantry.html", rows=rows, ingredients=ingredients)

@app.route("/mypantry/save/", methods=["POST"])
def save_ingredients():
    result = request.get_json()
    conn = sqlite3.connect("Database.db")
    c = conn.cursor()
    for value in result['values']:
        row = c.execute(''' SELECT id FROM Ingredient WHERE name LIKE ?; ''', (value,)).fetchone()
        for entry in row: 
            print(entry)
            c.execute(''' INSERT INTO UserIngredients(user, ingredient) VALUES (?, ?); ''', (session['uid'], entry))
            conn.commit()
    return redirect(url_for("get_user_pantry"))

@app.route("/dailyplan/")
def get_daily_plan():
    if(session.get("uid") is None):
        flash("Must Sign Into an Account")
        return redirect(url_for("login_get"))
    rows=[]
    mealIngs=[]
    return render_template("user_daily_plan.html", rows=rows, mealIngs=[])

@app.route("/dailyplan/", methods=["POST"])
def post_daily_plan():
    conn = sqlite3.connect("Database.db")
    c = conn.cursor()
    rows = c.execute(''' SELECT * FROM Meal; ''')

    conn2 = sqlite3.connect("Database.db")
    c2 = conn.cursor()
    mealIngs = c2.execute(''' 
    SELECT * FROM MealIngredients JOIN Ingredient ON MealIngredients.ingredient_id = Ingredient.id
     JOIN Meal ON Meal.id = MealIngredients.meal_id;
     ''').fetchall()
    return render_template("user_daily_plan.html", rows=rows, mealIngs=mealIngs)
