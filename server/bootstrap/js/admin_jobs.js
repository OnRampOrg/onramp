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
		window.location.href = "admin_jobs.html";
	};

	self.viewJobResults = function () {
		// figure out if this user can see the results...
		alert("results page not available");
	};

	self.removeOnServer = function () {
		alert("removing on server");
	};
}


function AdminJobsViewModel() {
	var self = this;
	self.username = sessionStorage['UserID'];
	self.userID = sessionStorage['UserID'];



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
		self.Jobslist.push(new Job({'JobID':1, 'User': 4, 'Workspace':1, 'PCE': 2, 'Module':1, 'RunName':'test1', 'Status':'Running', 'Runtime':'0:32'}));
		self.Jobslist.push(new Job({'JobID':2, 'User': 4, 'Workspace':1, 'PCE': 1, 'Module':1, 'RunName':'test2', 'Status':'Running', 'Runtime':'0:02'}));
		self.Jobslist.push(new Job({'JobID':3, 'User': 4, 'Workspace':1, 'PCE': 2, 'Module':2, 'RunName':'does it work?', 'Status':'Queued', 'Runtime':'--'}));

	});

}

// Activates knockout.js
ko.applyBindings(new AdminJobsViewModel());
