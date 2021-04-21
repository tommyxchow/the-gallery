// Establish a WebSocket connection with the server
const socket = new WebSocket('ws://' + window.location.host + '/websocket');

// Call the addMessage function whenever data is received from the server over the WebSocket
socket.onmessage = addMessage;

// Allow users to send messages by pressing enter instead of clicking the Send button
document.addEventListener("keypress", function (event) {
	if (event.code === "Enter") {
		sendMessage();
	}
});

// Read the name/comment the user is sending to chat and send it to the server over the WebSocket as a JSON string
// Called whenever the user clicks the Send button or pressed enter
function sendMessage() {
	const chatName = document.getElementById("chat-name").value;
	const chatBox = document.getElementById("chat-comment");
	const comment = chatBox.value;
	chatBox.value = "";
	chatBox.focus();
	if (comment !== "") {
		socket.send(JSON.stringify({
			'username': chatName,
			'comment': comment
		}));
	}
}

// Called when the server sends a new message over the WebSocket and renders that message so the user can read it
function addMessage(message) {
	console.log(message)
	const chatMessage = JSON.parse(message.data);
	let chat = document.getElementById('chat');
	chat.innerHTML += "<b>" + chatMessage['username'] + "</b>: " + chatMessage["comment"] + "<br/>";
}

function loadImage(id) {
	document.getElementsByName
	var imageName = document.getElementById(id).innerHTML

	var test = document.getElementById("display")
	test.src = "/image/" + id
	test.className = "gallery"
}

function sendIt() {
	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function () {
		if (this.readyState == 4 && this.status == 200) {
			jsonResponse = JSON.parse(this.responseText)
			users = ''
			for (i = 0; i < jsonResponse['online_users'].length; i++) {
				users += jsonResponse['online_users'][i] + '<br>'
			}
			document.getElementById('users').innerHTML = users;
		}
	};
	xhttp.open('GET', '/online');
	xhttp.send();
}