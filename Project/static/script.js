'use strict';
/* 1. show map using Leaflet library. (L comes from the Leaflet library) */

let greenIcon = L.divIcon({ className: 'green-icon' });
let markers = [];
let playerName = "";
const startbutton = document.getElementById('startButton');

const blueIcon = L.divIcon({className: 'blue-icon'});





const map = L.map('map', { tap: false });
L.tileLayer('https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
  maxZoom: 20,
  subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
}).addTo(map);
map.setView([60,24], 7);
const airportMarkers = L.featureGroup().addTo(map);

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
    createmarker();

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


 async function createmarker() {
    try {
        airportMarkers.clearLayers();
        const data = await update_data()
        let hyvis = data.hyvis_sijainti
        for (let airport of data.lentokentat) {

            const marker = L.marker([airport.latitude_deg, airport.longitude_deg]).addTo(map);
            console.log( airport.ident)
            console.log(`hyvis:${hyvis.ident}`);

            if (airport.ident === hyvis.ident) {
                marker.bindPopup(`<b>You are here: ${airport.airport_name}</b>`).openPopup();
                marker.openPopup();
                marker.setIcon(greenIcon);
            } else {
                marker.setIcon(blueIcon);
                const popupcontent = document.createElement('div');
                const h4 = document.createElement('h4');
                h4.innerHTML = airport.airport_name;
                popupcontent.appendChild(h4);
                const gobutton = document.createElement('button');
                gobutton.classList.add('button');
                gobutton.innerHTML = 'Fly here';
                popupcontent.appendChild(gobutton);
                marker.bindPopup(popupcontent);

                gobutton.addEventListener('click', () => {
                    updateGame(airport.latitude_deg, airport.longitude_deg)
                        .then(() => {
                         createmarker(airport.latitude_deg, airport.longitude_deg);
                             })
                                .catch(error => console.error("Error in updating game:", error));
});

            }


       airportMarkers.addLayer(marker)  }
    } catch (error) {
        console.error("Error in createmarker:", error);
    }
}


async function update_data() {
    try {
        const response = await fetch('http://127.0.0.1:5000/update_data', {
            method: 'GET',
            headers: {
                'Content-type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        console.log(data)
        return data;  // Palauttaa datan, jota käytetään funktion kutsujan toimesta
    } catch (error) {
        console.error("Error in update_data:", error);
        return null;  // Palauttaa null, jos tapahtuu virhe
    }
}

  async function updateGame(lat, long) {
  try {
    const response = await fetch('http://127.0.0.1:5000/flyTo/' + lat + '/' + long, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    const data = await response.json(); // Add await here
    return data;
  } catch (error) {
    console.error('Error:', error);
    throw error; // You can handle errors appropriately here
  }
}