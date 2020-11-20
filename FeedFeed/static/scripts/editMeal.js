var unitConversions = {
    "Gal":128,
    "Qt": 32,
    "Cup": 8.115,
    "Oz": 1,
    "Tsp": 0.1667,
    "Tbsp": 0.5,
    "Lbs": 16
}

window.addEventListener("DOMContentLoaded", function() {

    document.getElementById("AddIngredient").addEventListener("click", cloneRow);

    document.getElementById("mealServes").addEventListener("keyup", calcCals)

    for (elt of document.querySelectorAll(".ing")) {
        elt.addEventListener("change", updateCals)
        elt.addEventListener("keyup", updateCals)
    }

});

function cloneRow() {
    var table = document.getElementById("ingTable");
    var firstRow = document.querySelector("tr.ingSelection");
    
    var rowClone = firstRow.cloneNode(true);

    //Reset attributes, add listeners
    var quant = rowClone.firstElementChild;
    quant.firstElementChild.firstElementChild.value = false;
    quant.firstElementChild.firstElementChild.addEventListener("keyup", updateCals);

    var units = quant.nextElementSibling;
    for (opt of units.firstElementChild.firstElementChild.children) {
        if(opt.selected) {
            opt.selected = false;
        }
    }
    units.firstElementChild.firstElementChild.firstElementChild.selected = true;
    units.firstElementChild.firstElementChild.addEventListener("change", updateCals);

    var ingredients = units.nextElementSibling;
    for (opt of ingredients.firstElementChild.firstElementChild.children) {
        if(opt.selected) {
            opt.selected = false;
        }
    }
    ingredients.firstElementChild.firstElementChild.firstElementChild.selected = true;
    ingredients.firstElementChild.firstElementChild.addEventListener("change", updateCals);

    var button = ingredients.nextElementSibling;
    button.firstElementChild.firstElementChild.disabled = false;
    button.firstElementChild.firstElementChild.addEventListener("click", removeIng);

    //Make sure the first row is clickable
    firstRow.lastElementChild.firstElementChild.firstElementChild.disabled = false;
    firstRow.lastElementChild.firstElementChild.firstElementChild.addEventListener("click", removeIng);

    //Put it out there
    table.appendChild(rowClone)

    //Scroll the scroll area to fit
    var childCnt = table.childElementCount;
    table.parentElement.scrollTop = 50 * childCnt;
}

function removeIng() {
    //Remove the row
    this.parentElement.parentElement.parentElement.remove();

    //Disable delete for first row if one left
    rows = document.querySelectorAll("tr.ingSelection");
    if(rows.length == 1) {
        rows[0].lastElementChild.firstElementChild.firstElementChild.disabled = true;
        rows[0].lastElementChild.firstElementChild.firstElementChild.removeEventListener("click", removeIng);
    }

    updateCals();
}

function calcCals() {
    var serves = this.value;

    computeCals(serves)
}

function updateCals() {
    computeCals(document.getElementById("mealServes").value);
}

function computeCals(serves) {
    if(serves != NaN && serves > 0) {
        var runningSum = 0;
        var addedIngs = document.querySelectorAll("option.ingOption");
        for (ing of addedIngs) {
            if (ing.selected) {
                //Get quantity
                var unitsParent = ing.parentElement.parentElement.parentElement.previousElementSibling;
                var quantParent = unitsParent.previousElementSibling;

                var unitsVal = unitsParent.firstElementChild.firstElementChild.value
                var quantVal = parseFloat(quantParent.firstElementChild.firstElementChild.value)

                runningSum += unitConversions[unitsVal] * quantVal * parseFloat(ing.getAttribute("data-calCount"));
            }
                
        }

        document.getElementById("caloriesPer").value = (Math.round((runningSum / serves) * 100) / 100);
    }
}