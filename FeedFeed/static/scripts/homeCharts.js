window.addEventListener("DOMContentLoaded", function() {
    var userDataChart = document.getElementById("userIngredients");
    var mealDataChart = document.getElementById("mealIngredients")

    var userDataElem = document.getElementsByClassName("uIngData");
    var mealDataElem = document.getElementsByClassName("mIngData");

    var userData = {
        datasets: [{
            data: []
        }],
        labels:[]
    };
    var mealData = {
        datasets: [{
            data: []
        }],
        labels:[]
    };

    for (d of userDataElem) {
        userData.labels.push(d.getAttribute("data-name"));
        userData.datasets.data.push(getAttribute("data-count"));
    }

    for (d of mealDataElem) {
        mealData.labels.push(d.getAttribute("data-name"));
        mealData.datasets.data.push(getAttribute("data-count"));
    }

    constructPie(userDataChart, userData);
    constructPie(mealDataChart, mealData);

});

function constructPie(elem, data) {
    var myPieChart = new Chart(elem, {
        type: 'pie',
        data: data,
        options: options
    });
}