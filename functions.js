function loadImage(id){
	console.log(id)
	document.getElementsByName
	var imageName = document.getElementById(id).innerHTML

	var test = document.getElementById("display")
	test.src = "/image/" + id + ".jpg"
	test.className = "gallery"
}