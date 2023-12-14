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
      console.log(data)
    createmarker();




  document.getElementById("player-modal").style.display = "none";
});
});


 async function createmarker() {
    try {
        airportMarkers.clearLayers();
        const data = await fetchUpdateData();
        fetchDirectionalHint();
        let hyvis = data.hyvis_sijainti
        for (let airport of data.lentokentat) {

            const marker = L.marker([airport.latitude_deg, airport.longitude_deg]).addTo(map);

            if (airport.ident === hyvis.ident) {
                marker.bindPopup(`<b>You are here: ${airport.airport_name}</b>`).openPopup();
                marker.openPopup();
                marker.setIcon(greenIcon);
                document.getElementById('player-location').innerHTML = `Airport name : ${airport.airport_name}`

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
                    updateGame(airport.ident)
                        .then(() => {
                         createmarker();
                             })
                                .catch(error => console.error("Error in updating game:", error));
});

            }


       airportMarkers.addLayer(marker)  }
    } catch (error) {
        console.error("Error in createmarker:", error);
    }
}


async function fetchUpdateData() {
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
        console.log(data);
        return data;
    } catch (error) {
        console.error("Error in fetchUpdateData:", error);
        return null;
    }
}
async function fetchDirectionalHint() {
    try {
        const hintResponse = await fetch('http://127.0.0.1:5000/directionalhint', {
            method: 'GET',
            headers: {
                'Content-type': 'application/json'
            }
        });

        if (!hintResponse.ok) {
            throw new Error(`HTTP error! Status: ${hintResponse.status}`);
        }

        const hintData = await hintResponse.json();
        document.getElementById('direction').innerHTML = hintData;
    } catch (error) {
        console.error("Error in fetchDirectionalHint:", error);
    }
}


  async function updateGame(ident) {
  try {
    const response = await fetch(`http://127.0.0.1:5000/flyTo/${ident}`, {
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