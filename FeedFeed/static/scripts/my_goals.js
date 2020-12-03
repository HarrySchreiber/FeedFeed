window.addEventListener("DOMContentLoaded", function() {
    let save_button = document.getElementById("save");
    save_button.addEventListener("click", saveData);
});

function saveData() {
    let heightFeet = document.getElementById("heightFeet").value;
    let heightInches = document.getElementById("heightInches").value;
    let weight = document.getElementById("weight").value;
    let cut = document.getElementById("cut-radio-button").checked;
    let maintain = document.getElementById("maintain-radio-button").checked;
    let bulk = document.getElementById("bulk-radio-button").checked;
    let exerciseGoal = document.getElementById("excercise-goal-box").value;
    const comment = {};
    if(heightFeet != "") {
        comment["height_feet"] = heightFeet;
    }
    if(heightInches != "") {
        comment["height_inches"] = heightInches;
    }
    if(weight != "") {
        comment["weight"] = weight;
    }
    if(cut) {
        comment["weight_goal"] = "cut";
    }
    if(maintain) {
        comment["weight_goal"] = "maintain";
    }
    if(bulk) {
        comment["weight_goal"] = "bulk";
    }
    if(exerciseGoal != "") {
        comment["exercise_goal"] = exerciseGoal;
    }
    console.log(comment);
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "http://127.0.0.1:5000/mygoals/save/");
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.addEventListener("load", function() {
        if(this.status < 400) {
            console.log("Successfully posted!");
        }
    });
    xhr.send(JSON.stringify(comment));
}