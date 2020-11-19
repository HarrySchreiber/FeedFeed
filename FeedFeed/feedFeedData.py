import os

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