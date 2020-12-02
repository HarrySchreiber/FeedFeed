var itemsSelected = []

window.addEventListener("DOMContentLoaded", function() {

    let dTable = document.getElementById("data-table");

    //Listen on checkboxes
    let checks = document.getElementsByClassName("dataCheck");

    for (check of checks) {
        check.addEventListener("change", function() {
            if (this.checked == true) {
                document.getElementById("selectAll").checked = true;
                document.getElementById("deleteAll").disabled = false;
                let elId = this.getAttribute("name");
                itemsSelected.push(elId);

                this.parentElement.parentElement.classList.add("table-primary");
            }
            if (this.checked == false) {
                let elId = this.getAttribute("name");
                let index = itemsSelected.indexOf(elId);

                if (index > -1) {
                    itemsSelected.splice(index, 1);
                }

                if (itemsSelected.length == 0) {
                    document.getElementById("selectAll").checked = false;
                    document.getElementById("deleteAll").disabled = true;
                }

                this.parentElement.parentElement.classList.remove("table-primary");
            }
        })
    }

    //Listen on delete buttons
    let deletes = document.getElementsByClassName("deleteBtn");

    for (btn of deletes) {
        btn.addEventListener("click", function() {
            deleteItem(this);
        });
    }

    //Attatch listener to modal delete button
    document.getElementById("deleteConfirm").addEventListener("click", function() {
        deleteAllSelected(this);
    });

    document.getElementById("selectAll").addEventListener("change", toggleSelection);
    document.getElementById("deleteAll").addEventListener("click", showModal);
});

function deleteItem(elt) {
    //Get item id
    let id = elt.parentElement.parentElement.firstElementChild.firstElementChild.getAttribute("name");

    if (!itemsSelected.includes(id))
        itemsSelected.push(id);

    showModal();
}

function showModal() {
    $("#deleteWarn").modal();
}

function deleteAllSelected(elt) {
    let type = elt.getAttribute("data-delete")

    for (id of itemsSelected) {
        console.log("Id to delete: " + id);
        // create a new XMLHttpRequest
        xhr = new XMLHttpRequest();

        if(type == "meal") {
            xhr.open("POST", "/dash/meals/remove/");
        }
        else if(type == "ingredient") {
            xhr.open("POST", "/dash/ingredients/remove/");
        }
        else {
            console.log("Error no item type defined");
            return;
        }
        
        xhr.setRequestHeader("Content-type","application/json");

        xhr.send(JSON.stringify({
            itemId: id
        }));
    }

    let items = document.getElementsByClassName("tData");

    for (item of items) {
        if (itemsSelected.includes(item.firstElementChild.firstElementChild.getAttribute("name"))) {
            item.classList.add("collapse")
        }
    }

    itemsSelected = []
}

function toggleSelection() {
    let items = document.getElementsByClassName("tData");

    if(itemsSelected.length > 0) {
        for(item of items) {
            if(item.firstElementChild.firstElementChild.checked) {
                item.firstElementChild.firstElementChild.checked = false;
                item.firstElementChild.firstElementChild.dispatchEvent(new Event("change"));
            }
        }
    }
    else {
        for (item of items) {
            item.firstElementChild.firstElementChild.checked = true;
            item.firstElementChild.firstElementChild.dispatchEvent(new Event("change"));
        }
    }
}