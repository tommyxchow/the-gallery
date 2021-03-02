function welcomeAlert(){
	alert("If you're seeing this, your server sent functions.js!")
	console.log("Test")
}

function loadImage(id){
	document.getElementsByName
	var imageName = document.getElementById(id).innerHTML

	var test = document.getElementById("display")
	test.src = "/image/" + id + ".jpg"
	test.className = "border"

}