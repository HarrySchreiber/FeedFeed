window.addEventListener("DOMContentLoaded", function() {
    let user_goals_form = document.getElementById("goal-info-signup");
    user_goals_form.addEventListener("submit", (e) => {
        let cut_radio = document.getElementById("cut-radio-button");
        let maintain_radio = document.getElementById("maintain-radio-button");
        let bulk_radio = document.getElementById("bulk-radio-button");
        let exercise_goal_box = document.getElementById("exercise-goal-box");

        if(cut_radio.value != "cut" || maintain_radio.value != "maintain" || bulk_radio.value != "bulk"){
            e.preventDefault();
            alert("Radio Selection must be either cut, maintain, or bulk");
        }
        
        if((cut_radio.checked ^ maintain_radio.checked ^ bulk_radio.checked) == 0){
            e.preventDefault();
            alert("Must only have 1 weight goal selected");
        }
        console.log(exercise_goal_box.value);


        if(exercise_goal_box.value != "1.2" && exercise_goal_box.value != "1.375" && exercise_goal_box.value != "1.55" && exercise_goal_box.value != "1.725" && exercise_goal_box.value != "1.9"){
            e.preventDefault();
            alert("Exercise goals can only have values of 1.2, 1.375, 1.55, 1.725, 1.9");
        }
    });
});