window.addEventListener("DOMContentLoaded", function() {
    let user_info_form = document.getElementById("user-info-signup");
    user_info_form.addEventListener("submit",(e) =>{
        let name = document.getElementById("name").value;
        let dob = document.getElementById("date-of-birth").value;
        let height_feet = document.getElementById("height-feet").value;
        let height_inches = document.getElementById("height-inches").value;
        let weight = document.getElementById("weight").value;

        if(name == "" || dob == "" || height_feet == "" || height_inches == "" || weight == ""){
            e.preventDefault();
            alert("Missing form field");
        }

        if(!/^\d{4}[\/\-](0?[1-9]|1[012])[\/\-](0?[1-9]|[12][0-9]|3[01])$/.test(dob)){
            e.preventDefault();
            alert("Date of birth is malformed");
        }

        if(Date()< Date(dob)){
            e.preventDefault();
            alert("Date must be before today");
        }
       
        if(Number.isNaN(parseInt(height_feet))){
            e.preventDefault();
            alert("Height in feet must be a number");
        }

        if(Number.isNaN(parseInt(height_inches))){
            e.preventDefault();
            alert("Height in inches must be a number");
        }

        if(Number.isNaN(parseInt(weight))){
            e.preventDefault();
            alert("Weight must be a number");
        }

        if(height_feet > 10 || height_feet < 1){
            e.preventDefault();
            alert("Height in feet Must be between 1 and 10");
        }

        if(height_inches > 12 || height_inches < 0){
            e.preventDefault();
            alert("Height in inches Must be between 0 and 12");
        }

        if(weight < 1 || weight > 1500){
            e.preventDefault();
            alert("Weight must be between 1 and 1500");
        }
            
        let male_gender = document.getElementById("male-gender");
        let female_gender = document.getElementById("female-gender");
        if(male_gender.value != "male" || female_gender.value != "female"){
            e.preventDefault();
            alert("Gender values must be either male or female");
        }

        if(male_gender.checked ^ female_gender.checked == 0){
            e.preventDefault();
            alert("Must select 1 option for gender");
        }
    });
});