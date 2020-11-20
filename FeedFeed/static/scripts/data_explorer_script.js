var itemsSelected = []

window.addEventListener("DOMContentLoaded", function() {

    let dTable = document.getElementById("data-table");

    //Listen on checkboxes
    let checks = document.getElementsByClassName("dataCheck");

    for (check of checks) {
        check.addEventListener("change", function() {
            if (this.checked == true) {
                let elId = this.getAttribute("name")
                itemsSelected.push(elId)

                this.parentElement.parentElement.classList.add("table-primary")
            }
            if (this.checked == false) {
                let elId = this.getAttribute("name")

                this.parentElement.parentElement.classList.remove("table-primary")
            }
        })
    }

});