var API_ENDPOINT = "<your-api-endpoint>";
var API_KEY = "<your-api-key>";

isEmpty = function(str) {
  return (!str || 0 === str.length);
};

createTableBody = function(records) {
  var newTableBody = document.createElement('tbody');
  for (let record of records) {
    insertRow(newTableBody, record);
  }

  return newTableBody;
};

insertRow = function(tableBody, record) {
  var player = "<audio controls><source src='" + record.url + "' type='audio/mpeg'></audio>";
  if (typeof record.url === "undefined") {
      player = "";
  }

  tableBody.insertAdjacentHTML('beforeend',
    "<tr>" +
		  "<td>" + record.voice + "</td>" +
		  "<td>" + record.created + "</td>" +
		  "<td>" + record.text + "</td>" +
		  "<td>" + player + "</td>" +
    "</tr>");

  return tableBody;
};

document.getElementById("say-it").onclick = function(){
  text = document.getElementById("record-text").value;
  text.trim();
  if (isEmpty(text)) {
    return;
  }

  fetch(API_ENDPOINT, {
    method: "POST",
    mode: "cors",
    headers: {
      "X-Api-Key": API_KEY,
      "Accept": "application/json",
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      text: text
    })
  })
  .then(function(response) {
    if (response.ok) {
      return response.json();
    }
  })
  .then(function(data) {
    var table = document.getElementById("last-record");
    var oldBody = table.getElementsByTagName('tbody')[0];
    var newBody = createTableBody(data);
    oldBody.parentNode.replaceChild(newBody, oldBody);
  })
  .catch(function(error) {
    console.log('There has been a problem with your fetch operation: ' + error.message);
    alert(error.message);
  });

  // Clear the text input
  document.getElementById("record-text").value = "";
  document.getElementById("char-counter").textContent="Characters: 0";
};

document.getElementById("refresh").onclick = function(){
  fetch(API_ENDPOINT + "/*", {
    method: "GET",
    mode: "cors",
    headers: {
      "X-Api-Key": API_KEY,
      "Accept": "application/json",
      "Content-Type": "application/json"
    }
  })
  .then(function(response) {
    if (response.ok) {
      return response.json();
    }
  })
  .then(function(data) {
    data.sort(function(a, b) {
        if (a.expires == b.expires) {
          return 0;
        }
        return a.expires < b.expires ? 1 : -1;
    });

    var table = document.getElementById("archives");
    var oldBody = table.getElementsByTagName('tbody')[0];
    var newBody = createTableBody(data);
    oldBody.parentNode.replaceChild(newBody, oldBody);
  })
  .catch(function(error) {
    console.log('There has been a problem with your fetch operation: ' + error.message);
    alert(error.message);
  });
};

document.getElementById("record-text").onkeyup = function(){
  if (event.keyCode == 13) {
    if(event.preventDefault) event.preventDefault();
    document.getElementById("say-it").click();
  }

  var length = document.getElementById("record-text").value.length;
	document.getElementById("char-counter").textContent="Characters: " + length;
};
