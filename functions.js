socket = new WebSocket('ws://' + window.location.host + '/websocket');

function loadImage(id) {
	document.getElementsByName
	var imageName = document.getElementById(id).innerHTML

	var test = document.getElementById("display")
	test.src = "/image/" + id
	test.className = "gallery"
}