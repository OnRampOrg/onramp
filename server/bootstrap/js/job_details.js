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
}



function JobDetailsViewModel() {
	var self = this;
	self.username = ko.observable("test");  // want to get this from the cookie/session/server
	self.userID = sessionStorage['UserID'];
	self.auth_data = sessionStorage['auth_data'];
	self.selectedJob = ko.observable();
	self.Jobslist = ko.observableArray();

	self.welcome =   "Welcome " + self.username();
	self.selectedFile = ko.observable("test.txt");

	$(document).ready( function () {

		// get jobs for this user
		$.getJSON( "http://flux.cs.uwlax.edu/onramp/api/users/" + self.userID + "/jobs?apikey=" + JSON.parse(self.auth_data).apikey,
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

	self.selectFile = function () {
		self.selectedFile(this);
	}

	self.selectJob = function (){
		self.selectedJob(this);
	}


}

// Activates knockout.js
ko.applyBindings(new JobDetailsViewModel());
