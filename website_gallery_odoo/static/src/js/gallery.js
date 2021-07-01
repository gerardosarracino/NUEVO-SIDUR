window.onload = function () {
	document.getElementById("myImg").onclick = function () {
		var myModal = document.getElementById("myModal");
		var modalImg = document.getElementById("modalImg");
		var captionText = document.getElementById("captionText");
		console.log(myModal);
		myModal.style.display = "block";
		modalImg.src = this.src;
		captionText.innerHTML = this.alt;

		var span = document.getElementsByClassName("close")[0];

		// When the user clicks on <span> (x), close the modal
		span.onclick = function () {
			myModal.style.display = "none";
		}
	}
}