function UserProfile(data) {
	var self = this;
	self.id = ko.observable(data['user_id']);
	self.username = ko.observable(data['username']);
	self.fullName = ko.observable(data['full_name']);
	self.email = ko.observable(data['email']);
	self.isAdmin = ko.observable(data['is_admin']);
	self.isEnabled = ko.observable(data['is_enabled']);
	self.password = ko.observable('dummyPassword');

	self.auth_data = sessionStorage['auth_data'];
	self.complete_func = function (data){
	      // packet structure:
	      //   data.status = the status code (200 is good)
	      //   data.responseText = the JSON data from the server
	      //     data.responseText.status = server's status code (0 = successful login)
	      //     data.responseText.status_message = server's status message
	      //     data.responseText.auth = JSON object with authentication info (NEED TO SEND WITH ALL FUTURE CALLS)
	      //     data.responseText.auth.username = username
	      //     data.responseText.auth.apikey = special code to know that this user is authenticated
	      //     data.responseText.auth.user_id = user id from the server
	      //     data.responseText.auth.session_id = session id used by the server
	      console.log(JSON.stringify(data));
	      console.log(data.responseText);
	      console.log(data["responseText"]);
	      console.log(data.status + 5);
	      if(data.status == 200){
	        alert("Success!");
	      }
	      else if(data.status == 401){
	        alert("Incorrect login info.  Please try again, or contact the admin to create or reset your account.");
	      }
	      else {
	        alert("Something went wrong with the sending or receiving of the ajax call.  Status code: " + data.status);
	      }

	};

	self.updateServer = function () {
		// this will push the user info to the server as a new user

	}
}


function UserProfileViewModel () {
	var self = this;

	self.username = ko.observable("test");
	self.fullName = ko.observable("4");
	self.email = ko.observable("5");
	self.isAdmin = ko.observable(false);
	self.auth_data = sessionStorage['auth_data'];
	self.userID = sessionStorage['UserID'];
	
	self.counter = ko.observable(0);

	self.toggleAdmin = function () {
		var newVal = !self.isAdmin();
		self.isAdmin(newVal);
	}


	self.updateServer = function () {
		alert("not implemented on server.");
		/*
		$.ajax({
		  type: 'PUT',
		  url: 'http://flux.cs.uwlax.edu/onramp/api/user?apikey=' + JSON.parse(this.auth_data).apikey,
		  //data: JSON.stringify({'password':this.password(), 'username':this.username(), 'is_admin':this.isAdmin(), 'is_enabled':this.isEnabled(), 'email':this.email(), 'full_name':this.fullName()}),
		  data: JSON.stringify({'auth': JSON.parse(self.auth_data), 'username':this.username(), 'is_admin':this.isAdmin(), 'email':this.email(), 'full_name':this.fullName()}),
		  complete: self.complete_func,
		  dataType: 'application/json',
		  contentType: 'application/json'
		} );
		*/
	}


	$(document).ready( function () {
		// get data from server

		$.getJSON( "http://flux.cs.uwlax.edu/onramp/api/users/" + self.userID + "?apikey=" + JSON.parse(self.auth_data).apikey,
			function (data){
			// {"status": 0,
			//  "status_message": "Success",
			//  "users": {
			//    "fields": ["user_id", "username", "full_name", "email", "is_admin", "is_enabled"],
			//    "data": [2, "alice", "", "", 0, 1]}}
			console.log(data);
			self.username(data.users.data[1]);
			self.fullName(data.users.data[2]);
			self.email(data.users.data[3]);
			self.isAdmin(data.users.data[4]);

			sessionStorage['UserName'] = self.username();
			}
		);



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
