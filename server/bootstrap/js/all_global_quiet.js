function PCE(data, view){
	var self = this;
	self.id = data['pce_id'];
	self.name = data['pce_name'];
	self.status = data['state'];
	//self.nodes = data['nodes'];
	//self.corespernode = data['corespernode'];
	//self.mempernode = data['mempernode'];
	self.description = data['description'];
	self.location = data['location'];
	self.modules = ko.observableArray();
	
	if( view ){
		self.viewPCE = function () {
			// go to manage Workspaces page and show this job
			window.location.href = "admin_pces.html";
		}
	}
}

function Job(data, view, details){
	var self = this;
	self.id = data['job_id'];
	self.user = data['user_id'];
	self.ws = data['workspace_id'];
	self.pce = data['pce_id'];
	self.mod = data['module_id'];
	self.name = data['job_name'];
	self.status = data['state'];
	self.time = "0:00";  // not implemented yet
	
	if( view ){
		self.viewJob = function () {
			// go to manage Jobs page and show this job
			window.location.href = "admin_jobs.html";
		};
	}
	if(details){
		self.gotoJobDetails = function () {
			window.location.href = "job_details.html";
		}
	}
	
}

function Module(data, view){
	var self = this;
	self.id = data['module_id'];
	self.name = data['module_name'];
	self.desc = data['description'];
	self.formFields = ko.observableArray();
	self.PCEs = ko.observableArray();

	self.addDefaultFormFields = function () {
		this.formFields.push({"field": "name", "value": "test"});
		this.formFields.push({"field": "nodes", "value": 1});
		this.formFields.push({"field": "processes", "value": 4});
	}
	
	if( view ){
		self.viewModule = function () {
			// go to manage users page and start with this user
			window.location.href = "admin_modules.html";
		};
	}
}


function Workspace(data, view){
	var self = this;
	self.id = data['workspace_id'];
	self.name = data['workspace_name'];
	self.desc = data['description'];


	self.captureWSID = function() {
		sessionStorage.setItem("WorkspaceID", this.id);
		//alert("workspace " + localStorage.getItem('WorkspaceID'));
		window.location.href = "workspace_quiet.html";
		
	}
	
	if( view ){
		self.viewWorkspace = function () {
		// go to manage Workspaces page and show this job
		window.location.href = "admin_workspaces.html";
		};
	}
}

self.logout = function (){

	// send post to server
	$.ajax({
	  type: 'POST',
	  url: 'http://flux.cs.uwlax.edu/onramp/api/logout',
	  data: self.auth_data,
	  complete: function () {
		  window.location.href = "start.html";
	  },
	  dataType: 'application/json',
	  contentType: 'application/json'
	} );

}