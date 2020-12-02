window.addEventListener("DOMContentLoaded", function() {
    let login_toggle_button = document.getElementById("log-in-radio");
    let signup_toggle_button = document.getElementById("sign-up-radio");
    login_toggle_button.addEventListener("click",toggle_login);
    signup_toggle_button.addEventListener("click",toggle_signup);
    let signup_form = document.getElementById("signup-form");
    signup_form.addEventListener("submit", (e) => {
        let signup_password = document.getElementById("signup-password").value;
        let signup_confirm_password = document.getElementById("signup-confirm-password").value;
        let signup_email = document.getElementById("signup-email").value;
        if(signup_password == "" || signup_confirm_password == "" || signup_email == ""){
            e.preventDefault();
            alert("Missing form field");
        }

        if(signup_password != signup_confirm_password){
            e.preventDefault();
            alert("Passwords Don't Match");
        }

        if(!/^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/.test(signup_email)){
            e.preventDefault();
            alert("Email is Malformed");
        }
    });
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