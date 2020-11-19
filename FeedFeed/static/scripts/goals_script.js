window.addEventListener("DOMContentLoaded", function() {
    let save_button = document.getElementById("save_button");
    save_button.addEventListener("click", save_changes);
});

function save_changes() {
    let height_feet = document.getElementById("height-feet");
    let height_inches = document.getElementById("height-inches");

    alert("Changes have been saved");
}
