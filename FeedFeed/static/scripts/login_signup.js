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
    let login_table_cell = document.getElementById("login-table-cell");
    login_table_cell.style.borderBottom = "none";
    let signup_table_cell = document.getElementById("signup-table-cell");
    signup_table_cell.style.borderBottom = "1px solid black";
}

function toggle_signup(){
    let login_form = document.getElementById("login-form");
    login_form.style.display = "none";
    let signup_form = document.getElementById("signup-form");
    signup_form.style.display =  "block";
    let login_table_cell = document.getElementById("login-table-cell");
    login_table_cell.style.borderBottom = "1px solid black";
    let signup_table_cell = document.getElementById("signup-table-cell");
    signup_table_cell.style.borderBottom = "none";
}