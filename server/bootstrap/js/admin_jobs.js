/*
 * Interface for admin to do things to jobs is not implemented on server
 */

function Job(data){
	var self = this;
	self.jID = data['JobID'];
	self.user = data['User'];
	self.ws = data['Workspace'];
	self.pce = data['PCE'];
	self.mod = data['Module'];
	self.name = data['RunName'];
	self.status = data['Status'];
	self.time = data['Runtime'];

	self.viewJob = function () {
		// go to manage Jobs page and show this job
		window.location.href = "job_details.html";
	};

	self.viewJobResults = function () {
		// figure out if this user can see the results...
		alert("results page not available");
	};

	self.removeOnServer = function () {
		alert("removing on server - not implemented yet");
	};
}


function AdminJobsViewModel() {
	var self = this;
	self.username = sessionStorage['UserID'];
	self.userID = sessionStorage['UserID'];
	self.auth_data = sessionStorage['auth_data'];


	self.Jobslist = ko.observableArray();

	self.deleteJob = function () {
		// tell server to delete this user
		self.Jobslist.remove(this);
		this.removeOnServer();
	}


	$(document).ready( function () {
		// reinitialize values
		self.Jobslist.removeAll();

		// get data from server
		// get jobs for this user
		$.getJSON( sessionStorage.server + "/jobs?apikey=" + JSON.parse(self.auth_data).apikey,
								//self.auth_data,
								function (data){
									// {"status": 0,
									//  "status_message": "Success",
									//  "users": {
									//    "fields": ["user_id", "username", "full_name", "email", "is_admin", "is_enabled"],
									//    "data": [2, "alice", "", "", 0, 1]}}
									console.log(JSON.stringify(data));
									for (var x = 0; x < data.users.data.length; x++){
										var raw = data.users.data[x];
										console.log(raw);
										var conv_data = {};
										for(var i = 0; i < data.users.fields.length; i++){
											console.log("adding: " + data.users.fields[i] + " = " + raw[i]);
											conv_data[data.users.fields[i]] = raw[i];
										}
										self.Jobslist.push(new Job(conv_data));
									}
								}
							);

	});

	self.logout = function (){
		// send post to server
		$.ajax({
		  type: 'POST',
		  url: sessionStorage.server + '/logout',
		  data: self.auth_data,
		  complete: function () {
			  window.location.href = "start.html";
		  },
		  dataType: 'application/json',
		  contentType: 'application/json'
		} );

	}

}

// Activates knockout.js
ko.applyBindings(new AdminJobsViewModel());
