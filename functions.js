function loadImage(id){
	document.getElementsByName
	var imageName = document.getElementById(id).innerHTML

	var test = document.getElementById("display")
	test.src = "/image/" + id + ".jpg"
	test.className = "border"
}