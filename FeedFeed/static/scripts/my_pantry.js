
var myArray = [];

window.addEventListener("DOMContentLoaded", function() {
    let add_selected_button = document.getElementById("addSelected");
    add_selected_button.addEventListener("click", addToList)

    let submit_button = document.getElementById("search");
    submit_button.addEventListener("click", search);

    let save = document.getElementById("submit-button");
    save.addEventListener("click", generateRequest);
});

function addToList() {
    let selected = document.querySelectorAll(".check")
    let ingredient_list = document.getElementById("ingList");
    let list = ingredient_list.querySelectorAll("ul");
    selected.forEach(function(element) {
        if(element.checked) {
            var node = document.createElement("LI");
            var textNode = document.createTextNode(element.value);
            node.appendChild(textNode)
            ingredient_list.appendChild(node);
            myArray.push(element.value);
        }
    });
    selected.forEach(function(element) {
        element.checked = false;
    })
}

function search() {
    let ingredients = document.querySelectorAll("tr");
    let term = document.getElementById("search_text").value;
    for(i = 0; i < ingredients.length; i++) {
        if(!ingredients[i].innerText.includes(term)) {
            ingredients[i].style.display = "none";
        }
    }
    if(term == "") {
        for(i = 0; i < ingredients.length; i++) {
            ingredients[i].style.display = "block";
        }
    }
}

function generateRequest() {
    const comment = {
        "values": myArray
    };
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "http://127.0.0.1:5000/mypantry/save/");
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.addEventListener("load", function() {
        if(this.status < 400) {
            console.log("Successfully posted!");
        }
    });
    xhr.send(JSON.stringify(comment));
}