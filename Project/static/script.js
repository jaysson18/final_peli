'use strict';
/* 1. show map using Leaflet library. (L comes from the Leaflet library) */

let greenIcon = L.divIcon({ className: 'green-icon' });
let markers = [];
let playerName = "";
const startbutton = document.getElementById('startButton');
let marker = "";
async function removemarkers(){
   for (let marker of markers) {
    marker.remove();
}}
console.log(markers)


const map = L.map('map', { tap: false });
L.tileLayer('https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
  maxZoom: 20,
  subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
}).addTo(map);
map.setView([60,24], 7);


startbutton.addEventListener('click', (event) => {
  event.preventDefault();
  playerName = document.querySelector('#player-input').value;
  document.querySelector('#player-modal').classList.add('hide');
  document.getElementById('player-name').innerHTML = playerName
  fetch('http://127.0.0.1:5000/start', {
    method: 'POST',
    headers: {
      'Content-type': 'application/json'
    }
  })
  .then(response => response.json())
  .then(data => {
    createmarker(data);

    const heroLocation = {
      latitude: data.hyvis_sijainti.latitude_deg,
      longitude: data.hyvis_sijainti.longitude_deg,
      icao: data.hyvis_sijainti.ident,
      country: data.hyvis_sijainti.country_name,
      name: data.hyvis_sijainti.airport_name
    };
    document.getElementById('player-location').innerHTML = `Airport name : ${heroLocation.name}`

    // Fetch directional hints using heroLocation...
    fetch(`http://127.0.0.1:5000/directionalhint/${heroLocation.latitude}/${heroLocation.longitude}`, {
      method: 'GET',
      headers: {
        'Content-type': 'application/json'
      }
    })
    .then(response => response.json())
    .then(data => {
      document.getElementById('direction').innerHTML = data

    });

  document.getElementById("player-modal").style.display = "none";
});
});


  async function createmarker(data) {
    for (let i = 0; i <= 29; i++) {
      if (data.lentokentat[i].ident === data.hyvis_sijainti.ident) {
        marker = L.marker([data.hyvis_sijainti.latitude_deg, data.hyvis_sijainti.longitude_deg]).addTo(map);
        marker.setIcon(greenIcon)
        marker.bindPopup(`<b>You are here: ${data.hyvis_sijainti.airport_name}</b>`);
        marker.openPopup();
        markers.push(marker)
      } else {
        marker = L.marker([data.lentokentat[i].latitude_deg, data.lentokentat[i].longitude_deg]).addTo(map);
        const popupcontent = document.createElement('div');
        const h4 = document.createElement('h4');
        h4.innerHTML = data.lentokentat[i].airport_name;
        popupcontent.append(h4);
        const gobutton = document.createElement('button');
        gobutton.classList.add('button');
        gobutton.innerHTML = 'fly here';
        popupcontent.append(gobutton);
        marker.bindPopup(popupcontent);
        markers.push(marker);
        let latlng = "";
        let lat = "";
        let lng = "";
        marker.on('click', function (event) {
          // Extract coordinates from the event
          latlng = event.latlng;
          lat = latlng.lat;
          lng = latlng.lng;
          console.log(lat, lng)
        })

        gobutton.addEventListener('click', () => {
          updateGame(lat, lng)
        })

      }
    }}




// global variables
    const apiUrl = 'http://127.0.0.1:5000/';
    const startLoc = 'EFHK';
    const globalGoals = [];
    const airportMarkers = L.featureGroup().addTo(map);

// icons
    const blueIcon = L.divIcon({className: 'blue-icon'});

    async function updateGame(lat, long) {
      fetch('http://127.0.0.1:5000/flyTo/' + lat + '/' + long, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })
          .then(response => response.json())
          .then(data => {
            console.log(data)
            removemarkers(markers)
            createmarker(data)
          })
    }





