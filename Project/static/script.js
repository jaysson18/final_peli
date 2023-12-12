'use strict';
/* 1. show map using Leaflet library. (L comes from the Leaflet library) */

let markercount = 0;
const greenIcon = L.divIcon({ className: 'green-icon' });
let markers = [];
const startbutton = document.getElementById('startButton');

startbutton.addEventListener('click', () => {
  event.preventDefault();
    fetch('http://127.0.0.1:5000/start', {
      method: 'POST',
      headers: {
        'Content-type': 'application/json'
      }
  })
      .then(response => response.json())
      .then(data => {
        for(let i = 0; i <= 29; i++) {
        if(data.lentokentat[i].ident === data.hyvis_sijainti.ident){
           const marker = L.marker([data.lentokentat[i].latitude_deg, data.lentokentat[i].longitude_deg], { icon: greenIcon }).addTo(map);
           marker.bindPopup(`<b>You are here: ${data.hyvis_sijainti.airport_name}</b>`);
           marker.openPopup();
        }else {
          const marker = L.marker([data.lentokentat[i].latitude_deg, data.lentokentat[i].longitude_deg]).addTo(map);
          const popupcontent = document.createElement('div');
          const h4 = document.createElement('h4');
          h4.innerHTML = data.lentokentat[i].airport_name;
          popupcontent.append(h4);
          const gobutton = document.createElement('button');
          gobutton.classList.add('button');
          gobutton.innerHTML = 'fly here';
          popupcontent.append(gobutton);
          marker.bindPopup(popupcontent);
        }

        }
      })
  document.getElementById("player-modal").style.display = "none";

})


const map = L.map('map', { tap: false });
L.tileLayer('https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
  maxZoom: 20,
  subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
}).addTo(map);
map.setView([60,24], 7);


async function addMarkers(lat, long, index) {
  let marker = "marker" + index;
  markers[marker];
  markers[index] = L.marker([lat, long]).addTo(map);
  markercount += 1;
}


// global variables
const apiUrl = 'http://127.0.0.1:5000/';
const startLoc = 'EFHK';
const globalGoals = [];
const airportMarkers = L.featureGroup().addTo(map);

// icons
const blueIcon = L.divIcon({ className: 'blue-icon' });

// form for player name
document.querySelector('#player-form').addEventListener('submit', function (evt) {
  evt.preventDefault();
  const playerName = document.querySelector('#player-input').value;
  document.querySelector('#player-modal').classList.add('hide');
  gameSetup(`${apiUrl}newgame?player=${playerName}&loc=${startLoc}`);
});


// function to update game status
function updateStatus(status) {
  document.querySelector('#player-name').innerHTML = `Player: ${status.name}`;
  document.querySelector('#consumed').innerHTML = status.co2.consumed;
  document.querySelector('#budget').innerHTML = status.co2.budget;
}

// function to show weather at selected airport
function showWeather(airport) {
  document.querySelector('#airport-name').innerHTML = `Weather at ${airport.name}`;
  document.querySelector('#airport-temp').innerHTML = `${airport.weather.temp}°C`;
  document.querySelector('#weather-icon').src = airport.weather.icon;
  document.querySelector('#airport-conditions').innerHTML = airport.weather.description;
  document.querySelector('#airport-wind').innerHTML = `${airport.weather.wind.speed}m/s`;
}

// function to check if any goals have been reached
function checkGoals(meets_goals) {
  if (meets_goals.length > 0) {
    for (let goal of meets_goals) {
      if (!globalGoals.includes(goal)) {
        document.querySelector('.goal').classList.remove('hide');
        location.href = '#goals';
      }
    }
  }
}

// function to update goal data and goal table in UI
function updateGoals(goals) {
  document.querySelector('#goals').innerHTML = '';
  for (let goal of goals) {
    const li = document.createElement('li');
    const figure = document.createElement('figure');
    const img = document.createElement('img');
    const figcaption = document.createElement('figcaption');
    img.src = goal.icon;
    img.alt = `goal name: ${goal.name}`;
    figcaption.innerHTML = goal.description;
    figure.append(img);
    figure.append(figcaption);
    li.append(figure);
    if (goal.reached) {
      li.classList.add('done');
      globalGoals.includes(goal.goalid) || globalGoals.push(goal.goalid);
    }
    document.querySelector('#goals').append(li);
  }
}

// function to check if game is over
function checkGameOver(budget) {
  if (budget <= 0) {
    alert(`Game Over. ${globalGoals.length} goals reached.`);
    return false;
  }
  return true;
}

// function to set up game
// this is the main function that creates the game and calls the other functions


// event listener to hide goal splash
