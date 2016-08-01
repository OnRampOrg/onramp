/*
 * Interface for admin to do things to jobs is not implemented on server
 * comments
 */
//too different
function myJob(data){
	var self = this;
	self.jID = data['job_id'];
	self.user = data['user_id'];
	self.ws = data['workspace_id'];
	self.pce = data['pce_id'];
	self.mod = data['module_id'];
	self.name = data['job_name'];
	self.status = data['state'];
	self.time = data['Runtime'];
	self.output = data['output_file'];

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
									for (var x = 0; x < data.jobs.data.length; x++){
										var raw = data.jobs.data[x];
										console.log(raw);
										var conv_data = {};
										for(var i = 0; i < data.jobs.fields.length; i++){
											console.log("adding: " + data.jobs.fields[i] + " = " + raw[i]);
											conv_data[data.jobs.fields[i]] = raw[i];
										}
										self.Jobslist.push(new myJob(conv_data));
									}
								}
							);

	});


}

// Activates knockout.js
ko.applyBindings(new AdminJobsViewModel());
