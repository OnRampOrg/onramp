
self.JobDetails = function () {
	window.location.href = "/public/Jobs";
}

function UserDashboardViewModel() {
	var self = this;
	self.Workspacelist = ko.observableArray();
	self.Jobslist = ko.observableArray();

	$(document).ready( function () {


		// get jobs for this user
		$.ajax({
		    url: '/public/Dashboard/GetJobs/',
		    type:'GET',
		    dataType:'json',
		    success: function(data) {
		        for (var x = 0; x < data.jobs.length; x++){
                    var job_data = data.jobs[x];
                    self.Jobslist.push(new Job(job_data, false, true));
                }
		    }
		})

		/*
		    get workspaces for this user
		    This request is a GET because we can use the
		    request object itself from django to determine the
		    user and get data for just the logged in user.
        */
		$.ajax({
		    url: '/public/Dashboard/GetWorkspaces/',
		    type: 'GET',
		    dataType: 'json',
		    success: function(data) {
		        for (var x = 0; x < data.workspaces.length; x++){
                    var ws_data = data.workspaces[x];
                    self.Workspacelist.push(new Workspace(ws_data, false));
                }
		    }
		})

    });

}

// Activates knockout.js
ko.applyBindings(new UserDashboardViewModel());
