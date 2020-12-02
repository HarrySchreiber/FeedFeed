import os

unitOpts = ["Gal", "Qt", "Cup", "Tsp", "Tbsp", "Oz", "Lbs"]

class Ingredient:
    def __init__(self, id, name, calories, protein, carbs, fat, isMeal):
        self.id = id
        self.name = name
        self.calories = calories
        self.protein = protein
        self.carbs = carbs
        self.fat = fat
        self.isMeal = isMeal
    def __str__(self):
        return f"{self.id}: {self.name}, {self.calories}, {self.protein}, {self.carbs}, {self.fat}, {self.isMeal}"
    def __repr__(self):
        return f"Ingredient: {self.id}"

class Meal:
    def __init__(self, id, name, description, image, serves, caloriesPerServing, ingredients):
        self.id = id
        self.name = name
        self.description = description
        self.image = image
        self.serves = serves
        self.caloriesPerServing = caloriesPerServing
        self.ingredients = ingredients
    def __str__(self):
        return f"{self.id}: {self.name}, {self.description}, {self.image}, {self.serves}, {self.caloriesPerServing}"
    def __repr__(self):
        return f"Meal: {self.id}"

class MealIng:
    def __init__(self, ingId, name, quantity, units):
        self.ingId = ingId
        self.name = name
        self.quantity = quantity
        self.units = units
    def __str__(self):
        return f"{self.quantity} {self.units} {self.name}"
    def __repr__(self):
        return f"MealIngredient: {self.ingId} ({self.name})"