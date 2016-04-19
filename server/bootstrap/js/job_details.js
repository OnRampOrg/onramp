function Job(data){
	var self = this;
	self.jID = data['job_id'];
	self.user = data['user_id'];
	self.ws = data['workspace_id'];
	self.pce = data['pce_id'];
	self.mod = data['module_id'];
	self.name = data['job_name'];
	self.status = data['state'];
	self.time = "0:00";  // not implemented yet
	self.data_files = ko.observableArray(["test.out", "out.txt", "other"]);
	self.output = data['output_file'];
	self.output_str = ko.observable("test");
	self.state_str = data['state_str'];
}

function JobDetailsViewModel() {
	var self = this;
	self.userID = sessionStorage['UserID'];
	self.auth_data = sessionStorage['auth_data'];
	self.username = JSON.parse(self.auth_data).username;  // want to get this from the cookie/session/server

	self.selectedJob = ko.observable();
	self.Jobslist = ko.observableArray();

	self.jobStates = [];

	self.welcome =   "Welcome " + self.username;
	self.selectedFile = ko.observable("test.txt");

	self.refreshJobs = function () {
		self.selectedJob(null);
		self.Jobslist.removeAll();
		$.getJSON( sessionStorage.server + "/users/" + self.userID + "/jobs?apikey=" + JSON.parse(self.auth_data).apikey,
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
	}

	$(document).ready( function () {
		self.Jobslist.removeAll();
		// get jobs for this user
		$.getJSON( sessionStorage.server + "/users/" + self.userID + "/jobs?apikey=" + JSON.parse(self.auth_data).apikey,
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

		// get job states
		$.getJSON( sessionStorage.server + "/states/jobs?apikey=" + JSON.parse(self.auth_data).apikey,
			//self.auth_data,
			function (data){
				self.jobStates = data.jobs;
				console.log(self.jobStates);
			}
		);

	});

	self.selectFile = function () {

		self.selectedFile(this);
	}

	self.selectJob = function (){
	    self.selectedJob(this);
		$.getJSON(sessionStorage.server + "/jobs/" + this.jID + "?apikey=" + JSON.parse(self.auth_data).apikey,
			function (data) {
				this.output = data.jobs.output;
				this.state_str = data.jobs.state_str;
			}
		);
		$.getJSON(sessionStorage.server + "/jobs/" + this.jID + "/data?apikey=" + JSON.parse(self.auth_data).apikey,
			function (data) {
			      console.log(data.jobs);
			      //this.output_str = data.jobs;
			      self.selectedJob().output_str(data.jobs);
			      //self.selectedFile(self.selectedJob().output_str());
			      self.selectedFile(sessionStorage["server"] + "/../" + self.selectedJob().output_str());
			}
		);
	    //self.selectedJob(this);
	}

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
ko.applyBindings(new JobDetailsViewModel());
