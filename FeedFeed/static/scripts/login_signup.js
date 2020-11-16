window.addEventListener("DOMContentLoaded", function() {
    let login_button = document.getElementById("log-in-radio");
    let signup_button = document.getElementById("sign-up-radio");
    login_button.addEventListener("click",toggle_login);
    signup_button.addEventListener("click",toggle_signup);
});

function toggle_login(){
    let login_form = document.getElementById("login-form");
    login_form.style.display = "block";
    let signup_form = document.getElementById("signup-form");
    signup_form.style.display = "none";
}

function toggle_signup(){
    let login_form = document.getElementById("login-form");
    login_form.style.display = "none";
    let signup_form = document.getElementById("signup-form");
    signup_form.style.display =  "block";
}