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

    //Attatch listers to headers to sort by
    let headers = document.getElementsByClassName("sortHeader");
    for (header of headers) {
        header.addEventListener("click", function() {
            sortTable(parseInt(this.getAttribute("data-colNum")))
        })
    }
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

//Table sorting code from: https://www.w3schools.com/howto/howto_js_sort_table.asp
function sortTable(n, isNum) {
    var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
    table = document.getElementById("data-table");
    switching = true;
    // Set the sorting direction to ascending:
    dir = "asc";
    /* Make a loop that will continue until
    no switching has been done: */
    while (switching) {
      // Start by saying: no switching is done:
      switching = false;
      rows = table.rows;
      /* Loop through all table rows (except the
      first, which contains table headers): */
      for (i = 1; i < (rows.length - 1); i++) {
        // Start by saying there should be no switching:
        shouldSwitch = false;
        /* Get the two elements you want to compare,
        one from current row and one from the next: */
        x = rows[i].getElementsByTagName("TD")[n];
        y = rows[i + 1].getElementsByTagName("TD")[n];
        /* Check if the two rows should switch place,
        based on the direction, asc or desc: */
        if (dir == "asc") {
          if(isNum) {
            if (Number(x.innerHTML) > Number(y.innerHTML)) {
                shouldSwitch = true;
                break;
            }
          }
          else {
            if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                // If so, mark as a switch and break the loop:
                shouldSwitch = true;
                break;
            }
          }
        } else if (dir == "desc") {
            if(isNum) {
                if (Number(x.innerHTML) < Number(y.innerHTML)) {
                    shouldSwitch = true;
                    break;
                }
              }
              else {
                if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                    // If so, mark as a switch and break the loop:
                    shouldSwitch = true;
                    break;
                }
              }
        }
      }
      if (shouldSwitch) {
        /* If a switch has been marked, make the switch
        and mark that a switch has been done: */
        rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
        switching = true;
        // Each time a switch is done, increase this count by 1:
        switchcount ++;
      } else {
        /* If no switching has been done AND the direction is "asc",
        set the direction to "desc" and run the while loop again. */
        if (switchcount == 0 && dir == "asc") {
          dir = "desc";
          switching = true;
        }
      }
    }
  }