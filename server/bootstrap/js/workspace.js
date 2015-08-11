function PCE (data) {
	var self = this;

	self.ID = data['pce_id'];
	self.name = data['pce_name'];
	self.status = data['state'];
	//self.nodes = data['nodes'];
	//self.corespernode = data['corespernode'];
	//self.mempernode = data['mempernode'];
	self.description = data['description'];
	self.location = data['location'];
	self.modules = [];


}

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
}

function Module(data){
	var self = this;
	self.mID = data['module_id'];
	self.name = data['module_name'];
	self.desc = data['description'];
	self.formFields = ko.observableArray();
	self.PCEs = [];
}


function Workspace(data){
	var self = this;
	self.wID = data['workspace_id'];
	self.name = data['workspace_name'];
	self.desc = data['description'];


	self.captureWSID = function () {

		localStorage.setItem("WorkspaceID", self.wID);
		alert("workspace " + localStorage.getItem('WorkspaceID'));
		window.location.href = "workspace.html";
		return;
	}
}


function OnrampWorkspaceViewModel () {
	// Data
	var self = this;
	self.username = sessionStorage['UserName'];  // want to get this from the cookie/session/server
	self.userID = sessionStorage['UserID'];
	self.auth_data = sessionStorage['auth_data'];
	self.workspaceID = sessionStorage['WorkspaceID'];
	self.workspaceInfo = ko.observable();
	//self.workspaceInfo(new Workspace({'WorkspaceID': 1,
	//'WorkspaceName': 'default',
	//'Description':'My personal workspace'}));

	self.PCElist = ko.observableArray();
	self.Jobslist = ko.observableArray();
	self.Modulelist = ko.observableArray();

	self.allPCEs = [];
	self.allModules = [];

	self.welcome1 = ko.observable("not loaded yet");

	self.selectedPCE = ko.observable();
	self.selectedModule = ko.observable();

	$(document).ready( function () {
		// get data from server
		$.getJSON( "http://flux.cs.uwlax.edu/onramp/api/workspaces/" + self.workspaceID + "?apikey=" + JSON.parse(self.auth_data).apikey,
		function (data){
			// {"status": 0,
			//  "status_message": "Success",
			//  "users": {
			//    "fields": ["user_id", "username", "full_name", "email", "is_admin", "is_enabled"],
			//    "data": [2, "alice", "", "", 0, 1]}}
			var raw = data.workspaces.data;
			console.log(raw);
			var conv_data = {};
			for(var i = 0; i < data.workspaces.fields.length; i++){
				console.log("adding: " + data.workspaces.fields[i] + " = " + raw[i]);
				conv_data[data.workspaces.fields[i]] = raw[i];
			}
			self.workspaceInfo(new Workspace(conv_data));
			self.welcome1(self.username + "'s " + self.workspaceInfo().name + " workspace");
		}
		);

			$.getJSON( "http://flux.cs.uwlax.edu/onramp/api/workspaces/" + self.workspaceID + "/pcemodulepairs?apikey=" + JSON.parse(self.auth_data).apikey,
			//self.auth_data,
			function (data){
				// {"status": 0,
				//  "status_message": "Success",
				//  "users": {
				//    "fields": ["user_id", "username", "full_name", "email", "is_admin", "is_enabled"],
				//    "data": [2, "alice", "", "", 0, 1]}}
				console.log(JSON.stringify(data));
				var pairs = data.workspaces.data;
				var fields = data.workspaces.fields;
				for(var i = 0; i < pairs.length; i++){
					var pce = pairs[i][0];
					var mod = pairs[i][2];
					// get data for new pce and/or module
					if(!self.allPCEs[pce]){
						$.getJSON("http://flux.cs.uwlax.edu/onramp/api/pces/" + currPCEs[i] + "?apikey=" + JSON.parse(self.auth_data).apikey,
						function(data){
							var raw = data.pces.data;
							console.log(raw);
							var conv_data = {};
							for(var i = 0; i < data.pces.fields.length; i++){
								console.log("adding: " + data.pces.fields[i] + " = " + raw[i]);
								conv_data[data.pces.fields[i]] = raw[i];
							}
							self.allPCEs[pce] = new PCE(conv_data);
							self.allPCEs[pce].modules.push(mod);
						}
					);
				}
				else {
					self.allPCEs[pce].modules.push(mod);
				}
				if(!self.allModules[mod]){
					$.getJSON("http://flux.cs.uwlax.edu/onramp/api/modules/" + currMods[i] + "?apikey=" + JSON.parse(self.auth_data).apikey,
					function(data){
						var raw = data.modules.data;
						console.log(raw);
						var conv_data = {};
						for(var i = 0; i < data.modules.fields.length; i++){
							console.log("adding: " + data.modules.fields[i] + " = " + raw[i]);
							conv_data[data.modules.fields[i]] = raw[i];
						}
						self.allModules[mod] = new Module(conv_data);
						self.allModules[mod].PCEs.push(pce);
					}
				);
			}
			else {
				self.allModules[mod].PCEs.push(pce);
			}
		}
	}
);
}
);



// Behaviors
self.selectPCE = function (PCE) {
	self.selectedPCE(PCE);
	//self.selectedModule(null);
	self.Modulelist.removeAll();
	for(mod in PCE.modules){
		self.Modulelist.push(mod);
	}
}

self.selectModule = function (m) {
	self.selectedModule(m);
	self.PCElist.removeAll();
	for(pce in m.PCEs){
		self.PCElist.push(pce);
	}
}


self.changePCE = function () {
	self.selectedPCE(null);
}

self.changeModule = function () {
	self.selectedModule(null);
}

this.launchJob = function (formData){
	alert("Launching a job with the following data: " + formData);
	for(k in formData.formFields){
		console.log(k + " : " + formData[k]);
	}
}
/*
this.alpacaForm = function (formData) {
$.alpaca({
"data" : {
"name": "Diego Maradona",
"feedback": "Very impressive.",
"ranking": "excellent"
},
"schema": {
"title":"User Feedback",
"description":"What do you think about Alpaca?",
"type":"object",
"properties": {
"name": {
"type":"string",
"title":"Name"
},
"feedback": {
"type":"string",
"title":"Feedback"
},
"ranking": {
"type":"string",
"title":"Ranking",
"enum":['excellent','ok','so so']
}
}
},
"options": {
"form":{
"attributes":{
"action":"http://httpbin.org/post",
"method":"post"
},
"buttons":{
"submit":{}
}
},
"helper": "Tell us what you think about Alpaca!",
"fields": {
"name": {
"size": 20,
"helper": "Please enter your name."
},
"feedback" : {
"type": "textarea",
"name": "your_feedback",
"rows": 5,
"cols": 40,
"helper": "Please enter your feedback."
},
"ranking": {
"type": "select",
"helper": "Select your ranking.",
"optionLabels": ["Awesome!",
"It's Ok",
"Hmm..."]
}
}
},
"view" : "bootstrap-edit"
});
}*/

// load data from server




}


ko.applyBindings(new OnrampWorkspaceViewModel());
