function UserProfileViewModel () {
	var self = this;

	self.username = ko.observable("test");
	self.fullName = ko.observable("4");
	self.email = ko.observable("5");
	self.isAdmin = ko.observable(false);
	self.auth_data = ko.observable();

	self.counter = ko.observable(0);

	self.toggleAdmin = function () {
		var newVal = !self.isAdmin();
		self.isAdmin(newVal);
	}


	self.updateServer = function () {
		alert("updated data on server <ko> (" + self.username() + ", " + self.fullName() + ", " + self.email() + ")");
		//location.hash = "save";
	}


	$(document).ready( function () {
		// get data from server

		// some hard coded data for now...
		self.username("Matilda");
		self.fullName("Matilda the Dragon");
		self.email("mm29@gmail.com");
		self.isAdmin(false);
	});

	self.logout = function (){
		// send post to server
		$.ajax({
		  type: 'POST',
		  url: 'http://flux.cs.uwlax.edu/onramp/api/logout',
		  data: self.auth_data,
		  complete: function () {
			  window.location.href = "start.html";
		  },
		  dataType: 'application/json',
		  contentType: 'application/json'
		} );

	}

}

ko.applyBindings(new UserProfileViewModel());
