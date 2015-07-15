// This should be replaced by something actually secure at somepoint.

// This is a simple *viewmodel* - JavaScript that defines the data and behavior of your UI
function DummyLoginViewModel() {
    this.username = ko.observable("");
    this.password = ko.observable("");
	
	this.dummyValidate = function() {
		if(this.username() === "Matilda" && this.password() === "RubytheMonkey") {
			// Success!  User login
			alert("You have successfully logged in as a user!");
			window.location = "user_dashboard.html";
		}
		else if (this.username() === "Batilda" && this.password() === "NellietheCat") {
			// Success!  Admin login
			window.location = "admin_dashboard.html";
		}
		else {
			alert("Login unsuccessful: " + this.username() + " " + this.password());
		}
		
	}
}

// Activates knockout.js
ko.applyBindings(new DummyLoginViewModel());