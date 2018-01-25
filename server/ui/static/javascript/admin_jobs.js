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


    self.updateJob = function() {
	var data = {
	    'user': this.user(),
	    'workspace': this.ws(),
	    'pce': this.pce(),
	    'module': this.mod(),
	    'job_name': this.name(),
	    'state': this.status(),
	    'output_file': this.output()
	    // TODO run_parameters, files, runtime
	}
	if(this.id() == undefined) {
	    var url = '/admin/Jobs/Create/';
	    var type = 'POST';
	} else {
	    var url = '/admin/Jobs/Update/';
	    var type = 'PUT';
	}
	$.ajax({
	    url: url,
	    type: type,
	    data: data,
	    success: function(result) {
		if(result['status'] == 1) {
		    // Successful
		} else {
		    // Unsuccessful
		    alert(result['status_message']);
		}
	    }
	});
    }

    self.removeOnServer = function () {
	alert("removing on server - not implemented yet");
        $ajax({
	    type: "DELETE",
	    data: {"jobId": this.id()},
	    url: "admin/Jobs/Delete",
	    error: function (response) {
		alert(response["status_message"]);
	    }
        });
    };
}


function AdminJobsViewModel() {
    var self = this;
    self.username = sessionStorage['UserID'];
    self.userID = sessionStorage['UserID'];
    self.auth_data = sessionStorage['auth_data'];

    self.selectedJob = ko.observable();

    self.Jobslist = ko.observableArray();

    self.addJob = function () {
	var newJob = new JobProfile({'name': 'New Job'});
	self.JobList.push(newJob);
	self.selectedJob(newJob);
    }

    self.selectJob = function () {
	self.selectedJob(this);
    }

    self.deleteJob = function () {
	// Tell the server to remove this job
	self.Jobslist.remove(this);
	this.removeOnServer();
    }

    $(document).ready( function () {
	self.selectedJob(null)
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
	});
    });
}

// Activates knockout.js
ko.applyBindings(new AdminJobsViewModel());
