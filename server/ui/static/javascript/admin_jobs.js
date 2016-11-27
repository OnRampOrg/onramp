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
		window.location.href = "/Public/Jobs";
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
		// tell server to delete this job
		// TODO this isn't implemented
		self.Jobslist.remove(this);
//		this.removeOnServer();
	}


	$(document).ready( function () {
		// reinitialize values
		self.Jobslist.removeAll();

		// get data from server
		$.ajax({
		    url:'/admin/Jobs/All',
		    type:'GET',
		    dataType:'json',
		    success: function(response) {
		        for (var x = 0; x < response.jobs.length; x++){
                    var job_data = response.jobs[x];
                    self.Jobslist.push(new myJob(job_data));
                }
		    }
		})
	});


}

// Activates knockout.js
ko.applyBindings(new AdminJobsViewModel());
