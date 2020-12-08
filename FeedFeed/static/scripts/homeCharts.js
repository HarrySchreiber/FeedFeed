window.addEventListener("DOMContentLoaded", function() {
    var userDataChart = document.getElementById("userIngredients");
    var mealDataChart = document.getElementById("mealIngredients")

    var userDataElem = document.getElementsByClassName("uIngData");
    var mealDataElem = document.getElementsByClassName("mIngData");

    var userData = {
        datasets: [{
            data: [],
            backgroundColor: palette(['tol', 'qualitative'], userDataElem.length).map(function(hex) {
                return '#' + hex;
              })
        }],
        labels:[]
    };
    var mealData = {
        datasets: [{
            data: [],
            backgroundColor: palette(['tol', 'qualitative'], mealDataElem.length).map(function(hex) {
                return '#' + hex;
              })
        }],
        labels:[]
    };

    for (d of userDataElem) {
        userData.labels.push(d.getAttribute("data-name"));
        userData.datasets[0].data.push(parseInt(d.getAttribute("data-count")));
    }

    for (d of mealDataElem) {
        mealData.labels.push(d.getAttribute("data-name"));
        mealData.datasets[0].data.push(parseInt(d.getAttribute("data-count")));
    }

    console.log(mealData.backgroundColor);

    constructPie(userDataChart, userData);
    constructPie(mealDataChart, mealData);

});

function constructPie(elem, data) {
    var myPieChart = new Chart(elem, {
        type: 'doughnut',
        data: data,
        options: {
            responsive: true,
            legend: {
                display: false
            }
        }
    });
}