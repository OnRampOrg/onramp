


function UserProfile(data) {
	var self = this;
	self.id = data['user_id'];
	self.username = data['username'];
	self.fullName = data['full_name'];
	self.email = data['email'];
	self.isAdmin = data['is_admin'];
	self.isEnabled = data['is_enabled'];


	self.viewUser = function () {
		// go to manage users page and start with this user
		window.location.href = "admin_users.html";
	};

}

function AdminDashboardViewModel() {
	var self = this;
	self.username = ko.observable();
	self.userID = sessionStorage['UserID'];
	self.auth_data = sessionStorage['auth_data'];

	self.Userslist = ko.observableArray();
	self.Workspacelist = ko.observableArray();
	self.Jobslist = ko.observableArray();
	self.PCEslist = ko.observableArray();
	self.Moduleslist = ko.observableArray();

	self.welcome =   "Admin Panel: " + self.username();

	self.manageUsers = function () {
		window.location.href = "../Users";
	};

	self.manageJobs = function () {
		window.location.href = "../Jobs";
	};

	self.manageWorkspaces = function () {
		window.location.href = "../Workspaces";
	};

	self.managePCEs = function () {
		window.location.href = "../PCEs";
	};

	self.manageModules = function () {
		window.location.href = "../Modules";
	};

	$(document).ready( function () {
		// reinitialize values
		self.Userslist([]);
		self.Workspacelist([]);
		self.Jobslist([]);
		self.PCEslist([]);
		self.Moduleslist([]);

        // Get users and populate the table
        $.ajax({
            url:'/admin/Dashboard/GetUsers/',
            type:'GET',
            dataType: 'json',
            success: function(data) {
                // loop over the users in the response and push them to the array
                for (var x = 0; x < data.users.length; x++){
                    var user_data = data.users[x];
                    self.Userslist.push(new UserProfile(user_data));
                }
            }
        })

        // Get jobs and populate the table
        $.ajax({
            url:'/admin/Dashboard/GetJobs/',
            type:'GET',
            dataType: 'json',
            success: function(data) {
                // loop over the users in the response and push them to the array
                for (var x = 0; x < data.jobs.length; x++){
                    var job_data = data.jobs[x];
                    self.Jobslist.push(new Job(job_data, true, false));
                }
            }
        })

        // Get workspaces and populate the table
        $.ajax({
            url:'/admin/Dashboard/GetWorkspaces/',
            type:'GET',
            dataType: 'json',
            success: function(data) {
                // loop over the workspaces in the response and push them to the array
                for (var x = 0; x < data.workspaces.length; x++){
                    var workspace_data = data.workspaces[x];
                    self.Workspacelist.push(new Workspace(workspace_data, true));
                }
            }
        })

        // Get PCE's and populate the table
        $.ajax({
            url:'/admin/Dashboard/GetPces/',
            type:'GET',
            dataType: 'json',
            success: function(data) {
                // loop over the workspaces in the response and push them to the array
                for (var x = 0; x < data.pces.length; x++){
                    var pce_data = data.pces[x];
                    self.PCEslist.push(new PCE(pce_data, true));
                }
            }
        })


		// Get modules and populate the table
        $.ajax({
            url:'/admin/Dashboard/GetModules/',
            type:'GET',
            dataType: 'json',
            success: function(data) {
                // loop over the workspaces in the response and push them to the array
                for (var x = 0; x < data.modules.length; x++){
                    var module_data = data.modules[x];
                    self.Moduleslist.push(new Module(module_data, true));
                }
            }
        })

    });
}

// Activates knockout.js
ko.applyBindings(new AdminDashboardViewModel());
