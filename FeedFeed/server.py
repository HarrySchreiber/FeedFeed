#TODO: I'm pretty sure this is how were going to host our app, but I could be jumping the gun so not sure we'll use this
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, g, abort #TODO: Not sure all of these are nesessary yet, but well find out
import sqlite3
import base64
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from passlib.hash import argon2

serverdir = os.path.dirname(__file__)
pepfile = os.path.join(serverdir,"pepper.bin")
with open(pepfile, 'rb') as fin:
    key = fin.read()
    pep = Fernet(key)


from passlib.hash import bcrypt_sha256

from feedFeedData import Ingredient, Meal, unitOpts

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
    session["exercise-goal"] = request.form.get("exercise-goal")

    c = get_db().cursor()
    c.execute("""
        INSERT INTO User (email,password,name,dob,height_feet,height_inches,weight,gender,weight_goal,exercise_goal)
        VALUES (?,?,?,?,?,?,?,?,?,?);
    """,(session.get("email"),session.get("password"),session.get("name"),session.get("date-of-birth"),session.get("height-feet"),session.get("height-inches"),session.get("weight"),session.get("gender"),session.get("weight-goal"),session.get("exercise-goal")))
    get_db().commit()
    return redirect(url_for("get_user_home"))

@app.route("/dash/")
def adminHome():
    #Until we get user logins and db implementation, placeholder data will be used for testing/viewing styling
    return render_template("admin_home.html",
                            username="Administrator",
                            uiSectionName="Home",
                            showBackButton=False)

@app.route("/dash/meals/")
def adminMealManager():
    mealData = dict()

    c = get_db().cursor()

    t = c.execute("""
        SELECT id, name, description, image, serves, calories_per_serving FROM Meal;
    """).fetchall()

    for record in t:
        mealData[record[0]] = Meal(record[0], record[1], record[2], record[3], record[4], record[5])

    return render_template("admin_meals.html",
                            username="Administrator",
                            uiSectionName="Meals",
                            showBackButton=True,
                            backLink=url_for("adminHome"),
                            tableData = mealData)

@app.route("/dash/meals/edit/", methods=["GET"])
def adminEditMeal():
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
        flash("Action not implemented yet")
        return redirect(url_for("adminMealManager"))
    
    abort(404)

@app.route("/dash/meals/edit/", methods=["POST"])
def adminEditMealPost():
    return redirect(url_for("adminMealManager"))

#Displays all the ingredients in the database in a readable format and provides management options
@app.route("/dash/ingredients/")
def adminIngredientManager():
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
    print(f"Submitted ing with id {request.form.get('id')}, isMeal is: {request.form.get('isMeal')}")
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

            print(f"Id: {ingId}")

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

    elif ingId > 0:
        c.execute("""
           UPDATE Ingredient
           SET calories = ?, protein = ?, carbs = ?, fat = ?, is_meal = ?
           WHERE id == ?
        """, (data["calories"], data["protein"], data["carbs"], data["fat"], isMealVal, data["id"]))

    get_db().commit()

    return redirect(url_for("adminIngredientManager"))

@app.route("/home/")
def get_user_home():
    '''
    conn = sqlite3.connect("Meals.db")
    c = conn.cursor()
    '''
    #rows = c.execute(''' SELECT * FROM Meals ''')
    '''
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
    '''
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
