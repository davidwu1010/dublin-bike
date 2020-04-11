'use strict';

var stationId = 1;
var weekdayIndex = 1;
let weekdays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
var readyCharts = 0;
var predictionData;
var predictionChart;

function showPrediction(id) {

    $.getJSON('/api/prediction/' + id, data => {
        predictionData = data;
        var predict_data = data[weekdays[weekdayIndex].substring(0, 3)];

        var labels = predict_data.map(function (item) {
            return item.hour;
        });

        var data = predict_data.map(function (item) {
            return item.bike_predict;
        });

        predictionChart =
            createChart('bar', 'Available Bikes Prediction', labels, data, 'prediction-chart');
    });
}

function showHourly(id) {

    $.getJSON('/api/hourly/' + id, hourly_data => {

        var labels = hourly_data.map(function (item) {
            return item.hour;
        });

        var data = hourly_data.map(function (item) {
            return item.available_bike;
        });

        createChart('line', 'Hourly Average Bike Available', labels, data, "hourly-chart");
    });
}

function showDaily(id) {
    $.getJSON('/api/daily/' + id, daily_data => {
         console.log(daily_data);
        var labels = daily_data.map(function (item) {
            return item.day_of_week;
        });

        var data = daily_data.map(function (item) {
            return item.available_bike;
        });

        createChart('line', 'Daily Average Bike Available', labels, data, "daily-chart", 'rgba(75, 192, 192, 0.2)', 'rgba(75, 192, 192, 1)');
    });
}


function createChart(chartType, title, labels, data, elementId, backgroundColor='rgba(54, 162, 235, 0.2)', borderColor='rgba(54, 162, 235, 1)') {
    var chartConfig = {
        type: chartType,
        data: {
            labels: labels,
            datasets: [{
                label: title,
                data: data,
                backgroundColor: backgroundColor,
                borderColor: borderColor,
                borderWidth: 1
            }]
        },
        options: {
            animation: {
                onComplete: () => {
                    readyCharts += 1;
                    if (readyCharts == 3) {
                        $('#spinner').css('display', 'none');
                        $('#chart').removeClass('d-none');
                    }
                }
            },
            legend: {
                display: false
            },
            title: {
                position: 'top',
                display: true,
                text: title
            },
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true
                    }
                }]
            }
        }
    };
    var ctx = document.getElementById(elementId).getContext('2d');

    var chart = new Chart(ctx, chartConfig);
    return chart;
}

function clickHandler(id) {  // handler for click on markers or list items
    stationId = id;
    $.when(
        $.ajax('/api/stations/' + id),
        $.ajax('/api/weather/' + id)
    ).then((station, weather) => {
        document.body.style.cursor = 'default';
        showDetails(station[0].data, weather[0]);
        map.setCenter({lat: station[0].data.latitude,  // set map center to the clicked station
                       lng: station[0].data.longitude});
        const content = `
        <div>
            ${station[0].data.address}
        </div>
        `;
        infowindow.setPosition(circles.get(id).getCenter());
        infowindow.setContent(content);
        infowindow.open(map);
    }).then(() => {
        weekdayIndex = new Date().getDay();
        setWeekday();
        readyCharts = 0;
        showPrediction(id);
        showHourly(id);
        showDaily(id);
    });
}

function backHandler() {  // back from station details to list when clicked
    infowindow.close();
    $.getJSON('/api/stations/', data => showList(data));
}

function showDetails(station, weathers) {
    function renderWeathers(weathers) {
        function renderWeather(weather) {
            const content = `
            <div class="col">
                <div class="row">
                    <div class="col" >${weather.datetime}</div>
                </div>
                <div class="row">
                    <img src="https://www.weatherbit.io/static/img/icons/${weather.icon}.png">
                </div>
                <div class="row">
                    <div class="col" >${weather.temperature}°</div>
                </div>
            </div>
            `;
            return content;
        }

        function formatAMPM(date) {
            var hours = date.getHours();
            var ampm = hours >= 12 ? 'PM' : 'AM';
            hours = hours % 12;
            hours = hours ? hours : 12; // the hour '0' should be '12'
            return hours + ampm;
        }

        let weathersContent = '';

        weathers.current.datetime = "Now";
        weathersContent += renderWeather(weathers.current);

        var forecast = weathers.forecast;
        for (let i = 0; i < forecast.length && i <= 3; i++) {
            var date = new Date(forecast[i].datetime);
            forecast[i].datetime = formatAMPM(date);
            weathersContent += renderWeather(forecast[i]);
        }
        return weathersContent;
    }

    let content = `
        <div class="row" id="icon">
             <div class="col">
                <button onclick="backHandler()" type="button">Back</button>
             </div>
        </div>
        <div class="row" id="station">
             <div class="col" >
                <p id="station_info"><b>${station.site_names}</b><br>${station.address}<br>Station is ${station.status}
                     <br>${station.available_bike + "/" + station.bike_stand} bikes available</p>
            </div>
        </div>
        <div class="row" id="weather" >
            ${renderWeathers(weathers)}
        </div>
        <div class="row d-none" id="chart">
            <div class="col">
                <div class="row">
                    <div class="col" style="text-align: center;">
                    <b id="weekday">Monday</b>
                    </div>
                </div>
                <div class="row" id="prediction-chart-div">
                    <div class="col-1"  style="position: relative;">
                        <button class="preNextBtn" onclick="preBtnClick()">&laquo;</button>
                    </div>
                    <div class="col-10">
                        <canvas id="prediction-chart" class="zone"></canvas>
                    </div>
                    <div class="col-1" style="position: relative;">
                        <button class="preNextBtn" onclick="nextBtnClick()">&raquo;</button>
                    </div>
                </div>
                <div class="row" style="margin:20px 30px;">
                    <canvas id="hourly-chart" class="zone" ></canvas>
                </div>
                <div class="row" style="margin:20px 30px;">
                    <canvas id="daily-chart" class="zone"></canvas>
                </div>
            </div>
        </div>
        <div class="row flex-grow-1" id="spinner">
            <div class="col-12 d-flex justify-content-center">
                <div class="spinner-border text-primary align-self-center" style="width: 6rem; height: 6rem;" role="status">
                    <span class="sr-only">Loading...</span>
                </div>
            </div>
        </div>
        `;
    $('#sidebar').html(content);
}

function preBtnClick() {
    if ( weekdayIndex <= 0 ){
        weekdayIndex = 6;
    } else {
        weekdayIndex-=1;
    }
    setWeekday();
    reloadCanvas();
}

function nextBtnClick() {
    if ( weekdayIndex >= 6 ){
        weekdayIndex = 0;
    } else {
        weekdayIndex+=1;
    }
    setWeekday();
    reloadCanvas();
}

function setWeekday(){

    document.getElementById("weekday").innerHTML = weekdays[weekdayIndex];
}

function reloadCanvas() {
    const predict_data = predictionData[weekdays[weekdayIndex].substring(0, 3)];
    const labels = predict_data.map(({hour}) => hour );
    const data = predict_data.map(({bike_predict}) => bike_predict);

    predictionChart.data.labels = labels;
    predictionChart.data.datasets[0].data = data;
    predictionChart.update(0);
}

function showList(data) {
    function renderListItem(station) {
        let availability;
        if (station.status === 'OPEN') {
            const availableBikes = station.available_bike.toString();
            const bikeStand = station.bike_stand.toString();
            availability = `${availableBikes}/${bikeStand} bikes available`;
        } else {
            availability = "Closed";
        }

        const stationNumber = station.number.toString();
        const content = `
            <li class="list-group-item" id="station-${stationNumber}">
                <ul>
                    <li><b>${station.address}</b></li>
                    <li>${availability}</li>
                </ul>
            </li>
            `;
        return content;
    }

    let listItems = '';
    for (const station of data.data) {
        listItems += renderListItem(station);
    }

    document.getElementById('sidebar').innerHTML = `
        <div class="col">
                <button onclick="backHandler()" type="button">Dublin Bikes</button>
        </div>
        <ul class="list-group-flush p-0 vh-100" id="list">
            ${listItems}
        </ul>
        `;

    const items = $('#list').children();
    for (const li of items) {
        const id = parseInt(li.id.split('-')[1]);
        li.addEventListener('click', () => clickHandler(id));
        li.addEventListener('mouseenter', () => {
            li.classList.add('active');
            document.body.style.cursor = 'pointer';
        });
        li.addEventListener('mouseleave', () => {
            li.classList.remove('active');
            document.body.style.cursor = 'default';
        });
    }
}

var initMap = () => {

    //Check internet connection
    var status = navigator.onLine;
    if (status) {
        this.map = new google.maps.Map(
        document.getElementById('map'), {
            zoom: 15,
            center: {lat: 53.3568, lng: -6.26814},  // Blessington Street station
            fullscreenControl: false
        });

        this.infowindow = new google.maps.InfoWindow();

        // Try HTML5 geolocation.
        //Setting and Scrolling user's location
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function(position) {
            var pos = {
              lat: position.coords.latitude,
              lng: position.coords.longitude
            };
            // The marker, positioned at user location
            var marker = new google.maps.Marker({position: pos, map: map});
            map.setCenter(pos);
          }, function() {
            handleLocationError(true, infowindow, map.getCenter());
          });
        } else {
            // Browser doesn't support Geolocation
            handleLocationError(false, infowindow, map.getCenter());
        }
        this.circles = new Map();  // HashMap not Google Map

        $.getJSON('/api/stations/', data => {
            for (const station of data.data) {
                const availability = station.available_bike / station.bike_stand;

                let color;
                if (availability <= 0.1) {
                    color = 'red';
                } else if (availability <= 0.4) {
                    color = 'orange';
                } else {
                    color = 'green';
                }

                const circle = new google.maps.Circle({
                    strokeColor: 'white',
                    strokeOpacity: 0.4,
                    fillColor: color,
                    fillOpacity: 0.6,
                    map: this.map,
                    center: {
                        lat: station.latitude,
                        lng: station.longitude
                    },
                    radius: station.bike_stand * 2
                });
                circles.set(station.number, circle);
            }

            for (const pair of circles) {
                let [id, circle] = pair;
                circle.addListener('click', () => clickHandler(id));
            }

            showList(data);
            });
            $.getJSON('/api/weather/29', ( {current} ) => {
            const { description, icon, temperature } = current;
            $('#weather-widget-description').text(description);
            $('#weather-widget-icon').attr('src',
                `https://www.weatherbit.io/static/img/icons/${icon}.png`);
            $('#weather-widget-temperature').text(temperature + '°');
            $('#weather-widget').css('display', 'block');
            });
    //If no internet connection, show a alert
    } else {
        alert('No internet Connection! Please try again.');
    }
};


function handleLocationError(browserHasGeolocation, infoWindow, pos) {
    infowindow.setPosition(pos);
    infowindow.setContent('Blessington Street');
    infowindow.open(map);
}
