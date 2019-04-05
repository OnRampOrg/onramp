/*
 * Interface for admin to do things to jobs is not implemented on server
 * comments
 */
//too different
function myJob(data){
	var self = this;
	self.jID = ko.observable(data['job_id']);
	self.user = ko.observable(data['user_id']);
	self.ws = data['workspace_id'];
	self.pce = ko.observable(data['pce_id']);
	self.mod = ko.observable(data['module_id']);
	self.name = ko.observable(data['job_name']);
	self.status = data['state'];
	self.time = data['Runtime'];
	self.output = data['output_file'];
	self.formFields = ko.observableArray();

	self.viewJob = function () {
		// go to manage Jobs page and show this job
		window.location.href = "/Public/Jobs";
	};

	self.viewJobResults = function () {
		// figure out if this user can see the results...
		alert("results page not available");
	};

	self.addDefaultFormFields = function () {
		
	};

	self.removeOnServer = function () {
        alert("removing on server - not implemented yet");
        $.ajax({
            type: "DELETE",
            url: "jobs/" + this.id(),
            error: function (response) {
                alert(response["status_message"]);
            }
        });
	};

	self.postNewJobAjax = function () {
		console.log(data)
        $.ajax({
            type: "POST",
            url: "newjob/",
            error: function (response) {
                alert(response["status_message"]);
			},
			data: JSON.stringify({
				'module_id':this.mod(),
				'pce_id': this.pce(),
				'job_name':this.name(),
				'user': this.user()
			}),
			complete: function(){
				alert("job added");
			},
			dataType: 'application/json',
			contentType: 'application/json'
        });
	};
}


function AdminJobsViewModel() {
	var self = this;
	self.username = sessionStorage['UserID'];
	self.userID = sessionStorage['UserID'];
	self.auth_data = sessionStorage['auth_data'];

	self.selectedJob = ko.observable();
	self.newJob = ko.observable();

	self.Jobslist = ko.observableArray();
	
	

    self.showNewJobModal = function () 
		{
			self.selectedJob(null)
			console.log("NEW JOB CREATION!")
			self.newJob(new myJob({'pce_id': '1'}));
		}
	self.postNewJob = function (){
		console.log("TRYING TO ADD JOB");
		self.newJob().postNewJobAjax();
		self.newJob(null);
	}


    self.selectJob = function (job) {

    }

	self.deleteJob = function () {
		// tell server to delete this job
		// TODO this isn't implemented
		self.Jobslist.remove(this);
//		this.removeOnServer();
	}

	self.selectJob = function () {
		self.selectedJob(this);
	}

	self.refreshjobs = function (){
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
