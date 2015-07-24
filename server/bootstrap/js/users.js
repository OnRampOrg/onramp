// This should be replaced by something actually secure at somepoint.

// This is a simple *viewmodel* - JavaScript that defines the data and behavior of your UI
function DummyLoginViewModel() {
    this.username = ko.observable("");
    this.password = ko.observable("");
	sessionStorage["UserID"] = -999;
	sessionStorage["isAdmin"] = false;
	
	this.welcome = ko.computed( function() { return "Welcome " + this.username + "!";});
	
	this.dummyValidate = function() {
		if(this.username() === "Matilda" && this.password() === "RubytheMonkey") {
			// Success!  User login
			alert("You have successfully logged in as a user!");
			this.authenticated = true;
			sessionStorage.setItem('UserID', 123);
			window.location.href = "user_dashboard.html";
		}
		else if (this.username() === "Batilda" && this.password() === "NellietheCat") {
			// Success!  Admin login
			this.isAdmin = true;
			this.authenticated = true;
			sessionStorage['UserID']= 456;
			window.location.href = "admin_dashboard.html";
		}
		else {
			this.authenticated = false;
			alert("Login unsuccessful: " + this.username() + " " + this.password());
		}
		
	}
}

// Activates knockout.js
ko.applyBindings(new DummyLoginViewModel());