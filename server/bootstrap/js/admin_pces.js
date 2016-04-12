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


	self.viewJob = function () {
		// go to manage Jobs page and show this job
		window.location.href = "admin_jobs.html";
	};
}

function Workspace(data){
	var self = this;
	self.wID = data['workspace_id'];
	self.name = data['workspace_name'];
	self.desc = data['description'];


	this.captureWSID = function () {
		sessionStorage.setItem("WorkspaceID", this.wID);
		//alert("workspace " + localStorage.getItem('WorkspaceID'));
		window.location.href = "workspace.html";
	};

	self.viewWorkspace = function () {
		// go to manage Workspaces page and show this job
		window.location.href = "admin_workspaces.html";
	};

}

function PCE (data) {
	var self = this;

	self.id = ko.observable(data['pce_id']);
	self.name = ko.observable(data['pce_name']);
	self.status = ko.observable(data['state']);
	self.description = ko.observable(data['description']);
	self.location = ko.observable(data['location']);
	self.contact_info = ko.observable(data['contact_info']);
	self.pce_password = ko.observable(data['pce_password']);
	self.pce_username = ko.observable(data['pce_username']);
	self.port = ko.observable(data['port']);
	self.url = ko.observable(data['url']);
	self.from_server = data['from_server'];

	self.auth_data = sessionStorage['auth_data'];

	self.Workspacelist = ko.observableArray();
	self.Jobslist = ko.observableArray();
	self.Moduleslist = ko.observableArray();
	self.newModule = ko.observable();

	self.viewPCE = function () {
		// go to manage Workspaces page and show this job
		window.location.href = "admin_PCEs.html";
	};

	self.complete_func = function (data){
      // packet structure:
      //   data.status = the status code (200 is good)
      //   data.responseText = the JSON data from the server
      //     data.responseText.status = server's status code (0 = successful login)
      //     data.responseText.status_message = server's status message
      //     data.responseText.auth = JSON object with authentication info (NEED TO SEND WITH ALL FUTURE CALLS)
      //     data.responseText.auth.username = username
      //     data.responseText.auth.apikey = special code to know that this user is authenticated
      //     data.responseText.auth.user_id = user id from the server
      //     data.responseText.auth.session_id = session id used by the server
      console.log(JSON.stringify(data));
      console.log(data.responseText);
      console.log(data["responseText"]);
      console.log(data.status + 5);
      if(data.status == 200){
		  //self.id(data.pce.id);
		  //self.status(data.pce.state);
		  alert("Success!");
      }
      else if(data.status == 401){
        alert("Incorrect login info.  Please try again, or contact the admin to create or reset your account.");
      }
      else {
        alert("Something went wrong with the sending or receiving of the ajax call.  Status code: " + data.status);
      }

    };

	self.refreshModules = function (){
		// get modules for this user
		self.Moduleslist.removeAll();
		$.getJSON( sessionStorage.server + "/pces/" + self.id() + "/modules?apikey=" + JSON.parse(self.auth_data).apikey,
			//self.auth_data,
			function (data){
				// {"status": 0,
				//  "status_message": "Success",
				//  "users": {
				//    "fields": ["user_id", "username", "full_name", "email", "is_admin", "is_enabled"],
				//    "data": [2, "alice", "", "", 0, 1]}}
				console.log(JSON.stringify(data));
				for (var x = 0; x < data.pces.data.length; x++){
					var raw = data.pces.data[x];
					console.log(raw);
					var conv_data = {};
					for(var i = 0; i < data.pces.fields.length; i++){
						console.log("adding: " + data.pces.fields[i] + " = " + raw[i]);
						conv_data[data.pces.fields[i]] = raw[i];
					}
					self.Moduleslist.push(new Module(conv_data));
				}
			}
		);
	}

	self.refreshWorkspaces = function (){
		self.Workspacelist.removeAll();
		// get workspaces for this PCE
		$.getJSON( sessionStorage.server + "/pces/" + self.id() + "/workspaces?apikey=" + JSON.parse(self.auth_data).apikey,
			//self.auth_data,
			function (data){
				// {"status": 0,
				//  "status_message": "Success",
				//  "users": {
				//    "fields": ["user_id", "username", "full_name", "email", "is_admin", "is_enabled"],
				//    "data": [2, "alice", "", "", 0, 1]}}
				console.log(JSON.stringify(data));
				for (var x = 0; x < data.pces.data.length; x++){
					var raw = data.pces.data[x];
					console.log(raw);
					var conv_data = {};
					for(var i = 0; i < data.pces.fields.length; i++){
						console.log("adding: " + data.pces.fields[i] + " = " + raw[i]);
						conv_data[data.pces.fields[i]] = raw[i];
					}
					self.Workspacelist.push(new Workspace(conv_data));
				}
			}
		);
	}

	self.refreshJobs = function () {
		self.Jobslist.removeAll();
		$.getJSON( sessionStorage.server + "/pces/" + self.id() + "/jobs?apikey=" + JSON.parse(self.auth_data).apikey,
			//self.auth_data,
			function (data){
				// {"status": 0,
				//  "status_message": "Success",
				//  "users": {
				//    "fields": ["user_id", "username", "full_name", "email", "is_admin", "is_enabled"],
				//    "data": [2, "alice", "", "", 0, 1]}}
				console.log(JSON.stringify(data));
				for (var x = 0; x < data.pces.data.length; x++){
					var raw = data.pces.data[x];
					console.log(raw);
					var conv_data = {};
					for(var i = 0; i < data.pces.fields.length; i++){
						console.log("adding: " + data.pces.fields[i] + " = " + raw[i]);
						conv_data[data.pces.fields[i]] = raw[i];
					}
					self.Jobslist.push(new Job(conv_data));
				}
			}
		);
	}

	self.editPCE = function () {
		this.refreshJobs();
		this.refreshModules();
		this.refreshWorkspaces();
	}

	self.addModule = function () {
		// LEFT OFF HERE!!!!
		//   todo: need to fix ajax call, and figure out what the paths need to be
		// this will add a new module to the PCE
		// POST .../admin/pces/:ID/modules/:MODULEID
		console.log(self.newModule().name());
		console.log(self.newModule().id());
		self.newModule().id(self.Moduleslist().length + 1);
		$.ajax({
			type: 'POST',
			url: sessionStorage.server + '/admin/pce/' + self.id() + '/module/' + self.newModule().id() +'?apikey=' + JSON.parse(self.auth_data).apikey,
			//	"auth": { ...}, // Removed for brevity
    		//	"contact_info": "Someone else",
    		//	"description": "Secret Compute Resource",
    		//	"location": "Hidden Hallway",
    		//	"name": "Flux",
    		//	"pce_password": "fake123",
    		//	"pce_username": "onramp",
    		//	"port": 9071,
    		//	"url": "127.0.0.1"
			data: JSON.stringify({'auth': JSON.parse(self.auth_data),
				'module_id':self.newModule().id(),
				'module_name':self.newModule().name(),
				'install_location':self.newModule().install_location(),
				'src_location_type':self.newModule().src_location_type(),
				'src_location_path':self.newModule().src_location_path()
			}),
			complete: self.complete_func,
			dataType: 'application/json',
			contentType: 'application/json'
		} );
	}

	self.checkModuleStatus = function (mod) {
		// need to check
		// this will check the status of a module (GET .../admin/pces/:ID/modules/:MODULEID)
		// get workspaces for this PCE
		$.getJSON( sessionStorage.server + "/admin/pce/" + self.id() + "/module/" + mod.id() + "?apikey=" + JSON.parse(self.auth_data).apikey,
			//self.auth_data,
			function (data){
				// {"status": 0,
				//  "status_message": "Success",
				//  "users": {
				//    "fields": ["user_id", "username", "full_name", "email", "is_admin", "is_enabled"],
				//    "data": [2, "alice", "", "", 0, 1]}}
				console.log(JSON.stringify(data));
				for (var x = 0; x < data.pces.data.length; x++){
					var raw = data.pces.data[x];
					console.log(raw);
					//var conv_data = {};
					console.log("updating " + mod.name() + ": " + data.users.fields["state_str"] + " = " + raw["state_str"]);
					mod["state_str"](raw["state_str"]);
					mod["state"](raw["state"]);
				}
			}
		);
	}

	self.deployModule = function (mod) {
		// this will finish adding new module to the PCE
		// POST .../admin/pces/:ID/modules/:MODULEID
		$.ajax({
			type: 'POST',
			url: sessionStorage.server + '/admin/pce/' + self.id() + '/module/' + mod.id() +'?apikey=' + JSON.parse(self.auth_data).apikey,
			//	"auth": { ...}, // Removed for brevity
    		//	"contact_info": "Someone else",
    		//	"description": "Secret Compute Resource",
    		//	"location": "Hidden Hallway",
    		//	"name": "Flux",
    		//	"pce_password": "fake123",
    		//	"pce_username": "onramp",
    		//	"port": 9071,
    		//	"url": "127.0.0.1"
			data: JSON.stringify({'auth': JSON.parse(self.auth_data),
				'module_id':mod.id(),
				'module_name':mod.name(),
				'install_location':mod.install_location(),
				'src_location_type':mod.src_location_type(),
				'src_location_path':mod.src_location_path()
			}),
			complete: self.complete_func,
			dataType: 'application/json',
			contentType: 'application/json'
		} );
	}

	self.updateServer = function () {
		// this will add a new PCE
		$.ajax({
			type: 'POST',
			url: sessionStorage.server + '/admin/pce?apikey=' + JSON.parse(this.auth_data).apikey,
			//	"auth": { ...}, // Removed for brevity
    		//	"contact_info": "Someone else",
    		//	"description": "Secret Compute Resource",
    		//	"location": "Hidden Hallway",
    		//	"name": "Flux",
    		//	"pce_password": "fake123",
    		//	"pce_username": "onramp",
    		//	"port": 9071,
    		//	"url": "127.0.0.1"
			data: JSON.stringify({'auth': JSON.parse(self.auth_data),
				'contact_info':this.contact_info(),
				'description':this.description(),
				'location':this.location(),
				'name':this.name(),
				'pce_password':this.pce_password(),
				'pce_username':this.pce_username(),
				'port':this.port(),
				'url':this.url()
			}),
			complete: self.complete_func,
			dataType: 'application/json',
			contentType: 'application/json'
		} );
	}
	self.removeOnServer = function () {
		alert("remove on server not implmented");
	}
}



function Module(data){
	var self = this;
	self.id = ko.observable(data['module_id']);
	self.name = ko.observable(data['module_name']);
	self.state = ko.observable(data['state']);
	self.state_str = ko.observable(data['state_str']);
	self.install_location = ko.observable(data['install_location']);
	self.is_visible = ko.observable(data['is_visible']);
	self.src_location_path = ko.observable(data['src_location_path']);
	self.src_location_type = ko.observable(data['src_location_type']);
	self.desc = ko.observable(data['description']);
	self.formFields = ko.observableArray();
	self.PCEs = ko.observableArray();


	self.addDefaultFormFields = function () {
		this.formFields.push({"field": "name", "value": "test"});
		this.formFields.push({"field": "nodes", "value": 1});
		this.formFields.push({"field": "processes", "value": 4});
	};

	self.viewModule = function () {
		// go to manage users page and start with this user
		window.location.href = "admin_modules.html";
	};
}

function UserProfile(data) {
	var self = this;
	self.id = ko.observable(data['user_id']);
	self.username = ko.observable(data['username']);
	self.fullName = ko.observable(data['full_name']);
	self.email = ko.observable(data['email']);
	self.isAdmin = ko.observable(data['is_admin']);
	self.isEnabled = ko.observable(data['is_enabled']);
	self.password = ko.observable('dummyPassword');

	self.auth_data = sessionStorage['auth_data'];

	self.Workspacelist = ko.observableArray();
	self.Jobslist = ko.observableArray();
	self.Moduleslist = ko.observableArray();

	self.viewUser = function () {
		// go to manage users page and start with this user
		window.location.href = "admin_users.html";
	};

	self.editUser = function () {
		// get jobs for this user
		$.getJSON( sessionStorage.server + "/users/" + self.id() + "/jobs?apikey=" + JSON.parse(self.auth_data).apikey,
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

		// get workspaces for this user
		$.getJSON( sessionStorage.server + "/users/" + self.id() + "/workspaces?apikey=" + JSON.parse(self.auth_data).apikey,
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
					self.Workspacelist.push(new Workspace(conv_data));
				}
			}
		);
	};

	self.complete_func = function (data){
      // packet structure:
      //   data.status = the status code (200 is good)
      //   data.responseText = the JSON data from the server
      //     data.responseText.status = server's status code (0 = successful login)
      //     data.responseText.status_message = server's status message
      //     data.responseText.auth = JSON object with authentication info (NEED TO SEND WITH ALL FUTURE CALLS)
      //     data.responseText.auth.username = username
      //     data.responseText.auth.apikey = special code to know that this user is authenticated
      //     data.responseText.auth.user_id = user id from the server
      //     data.responseText.auth.session_id = session id used by the server
      console.log(JSON.stringify(data));
      console.log(data.responseText);
      console.log(data["responseText"]);
      console.log(data.status + 5);
      if(data.status == 200){
        alert("Success!");
      }
      else if(data.status == 401){
        alert("Incorrect login info.  Please try again, or contact the admin to create or reset your account.");
      }
      else {
        alert("Something went wrong with the sending or receiving of the ajax call.  Status code: " + data.status);
      }

    };

	self.updateServer = function () {
		// this will push the user info to the server as a new user
		$.ajax({
	      type: 'POST',
	      url: sessionStorage.server + '/admin/user?apikey=' + JSON.parse(this.auth_data).apikey,
	      //data: JSON.stringify({'password':this.password(), 'username':this.username(), 'is_admin':this.isAdmin(), 'is_enabled':this.isEnabled(), 'email':this.email(), 'full_name':this.fullName()}),
		  data: JSON.stringify({'auth': JSON.parse(self.auth_data), 'password':this.password(), 'username':this.username(), 'is_admin':this.isAdmin(), 'is_enabled':this.isEnabled(), 'email':this.email(), 'full_name':this.fullName()}),
	      complete: self.complete_func,
	      dataType: 'application/json',
	      contentType: 'application/json'
	  	} );
	}

	self.removeFromWorkspace = function () {
		// this is the workspace object
		self.Workspacelist.remove(this);
		alert("removing " + self.username() + " from workspace " + this.name);
	}

	self.removeOnServer = function () {
		alert("not implemented");
		/* * not implemented *
		alert("removing " + self.username() + " from the server.");

		$.ajax({
	      type: 'DELETE',
	      url: 'http://flux.cs.uwlax.edu/onramp/api/admin/user' + self.id,
	      data: JSON.stringify({'password':this.password(), 'username':this.username()}),
	      complete: self.complete_func,
	      dataType: 'application/json',
	      contentType: 'application/json'
	  	} );
	  */

	}

}



function AdminPCEViewModel() {
	var self = this;
	self.username = sessionStorage['UserID'];
	self.userID = sessionStorage['UserID'];
	self.auth_data = sessionStorage['auth_data'];

	self.newPCE = ko.observable();
	self.selectedPCE = ko.observable();
	self.PCElist = ko.observableArray();


	self.changePCE = function () {
		self.selectedPCE(null);
	};

	self.selectPCE = function () {
		self.selectedPCE(this);
		this.editPCE();
	}

	self.deletePCE = function () {
		// tell server to delete this user
		self.PCElist.remove(this);
		if (self.selectedPCE() == this) {
			self.selectedPCE(null);
		}
		this.removeOnServer();
	}

	self.addPCE = function () {
		// need to get user ID from the server, maybe not until data is populated?
		self.selectedPCE(null);
		self.newPCE(new PCE({"pce_id":-1, "pce_name":"name", "description":"description", "location":"location", "contact_info":"contact_info", "pce_username":"pce_username", "pce_password":"pce_password", "port":"port", "url":"url"}));
	}

	self.updateServer = function () {
		self.newPCE().updateServer();
		self.PCElist.push(self.newPCE);
		self.newPCE(null);
	}

	self.showNewModuleForm = function () {
		self.selectedPCE().newModule(new Module({"module_id": -1, "module_name":"new module", "state":-1, "state_str":"Creation in progress.", "install_location":"", "src_location_path":"", "src_location_type":""}));
	}

	$(document).ready( function () {
		// reinitialize values
		self.PCElist.removeAll();
		// get data from server
		// some hard coded data for now...
		$.getJSON( sessionStorage.server + "/pces?apikey=" + JSON.parse(self.auth_data).apikey,
			//self.auth_data,
			function (data){
				// {"status": 0,
				//  "status_message": "Success",
				//  "users": {
				//    "fields": ["user_id", "username", "full_name", "email", "is_admin", "is_enabled"],
				//    "data": [2, "alice", "", "", 0, 1]}}
				console.log(JSON.stringify(data));
				for (var x = 0; x < data.pces.data.length; x++){
					var raw = data.pces.data[x];
					console.log(raw);
					var conv_data = {};
					for(var i = 0; i < data.pces.fields.length; i++){
						console.log("adding: " + data.pces.fields[i] + " = " + raw[i]);
						conv_data[data.pces.fields[i]] = raw[i];
					}
					self.PCElist.push(new PCE(conv_data));
				}
			}
		);
		self.newPCE(null);
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
		});

	}

}

// Activates knockout.js
ko.applyBindings(new AdminPCEViewModel());
