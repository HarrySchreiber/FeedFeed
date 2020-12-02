#TODO: I'm pretty sure this is how were going to host our app, but I could be jumping the gun so not sure we'll use this
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, g, abort #TODO: Not sure all of these are nesessary yet, but well find out
import sqlite3

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

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

#Routes

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
