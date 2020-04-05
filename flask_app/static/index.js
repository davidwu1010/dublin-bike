'use strict';

var stationId = 1;
var weekdayIndex = 1;

function showPrediction(id) {

    $.getJSON('/api/hourly/' + id, predict_data => {

        var labels = predict_data.map(function (item) {
            return item.hour;
        });

        var data = predict_data.map(function (item) {
            return item.available_bike;
        });

        createChart('bar', 'Precidtion Bike Occupancy', labels, data, 'prediction-chart');
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
                <button onclick="backHandler()" type="button">Dublin_Bike</button>
             </div>
        </div>
        <div class="row" id="station">
             <div class="col" >
                <p id="station_info">${station.site_names}<br>${station.status}<br>${station.address}
                     <br>${station.available_bike + "/" + station.bike_stand} bikes available</p>
            </div>
        </div>
        <div class="row" id="weather" >
            ${renderWeathers(weathers)}
        </div>
        <div class="row" id="chart">
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
    let weekdays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    document.getElementById("weekday").innerHTML = weekdays[weekdayIndex];
}

function reloadCanvas(){
    const canvas = document.getElementById("prediction-chart");
    const context = canvas.getContext('2d');
    context.clearRect(0, 0, canvas.width, canvas.height);
    showPrediction(stationId);
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
                    <li>${station.address}</li>
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
                <button onclick="backHandler()" type="button">Dublin_Bike</button>
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
    this.map = new google.maps.Map(
        document.getElementById('map'), {
            zoom: 15,
            center: {lat: 53.342964, lng: -6.286889},  // dublin center
            fullscreenControl: false
        });

    this.infowindow = new google.maps.InfoWindow();
    this.circles = new Map();  // HashMap not Google Map
    $.getJSON('/api/stations/', data => {
        for (const station of data.data) {
            const color = station.available_bike / station.bike_stand > 0.2
                ? 'green' : 'red';
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
};
