function PCE (data) {
	var self = this;
	
	self.ID = data['ID'];
	self.name = data['name'];
	self.status = data['status'];
	self.nodes = data['nodes'];
	self.corespernode = data['corespernode'];
	self.mempernode = data['mempernode'];
	self.description = data['description'];
	
}

function Job(data){
	var self = this;
	self.jID = data['JobID'];
	self.ws = data['Workspace'];
	self.pce = data['PCE'];
	self.mod = data['Module'];
	self.name = data['RunName'];
	self.status = data['Status'];
	self.time = data['Runtime'];
}

function Module(data){
	var self = this;
	self.mID = data['ID'];
	self.name = data['name'];
	self.desc = data['details'];
	self.formFields = ko.observableArray();
	for(k in data['formFields']){
		self.formFields.push([k, data['formFields'][k]]);
	}
}


function Workspace(data){
	var self = this;
	self.wID = data['WorkspaceID'];
	self.name = data['WorkspaceName'];
	self.desc = data['Description'];
	
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
	self.username = sessionStorage['UserID'];  // want to get this from the cookie/session/server
	self.userID = sessionStorage['UserID'];
	self.workspaceID = sessionStorage['WorkspaceID'];
	self.workspaceInfo = ko.observable();
	self.workspaceInfo(new Workspace({'WorkspaceID': 1,
										   'WorkspaceName': 'default',
										   'Description':'My personal workspace'}));
		
	self.PCElist = ko.observableArray();
	self.Jobslist = ko.observableArray();
	self.Modulelist = ko.observableArray();
	
	
	self.selectedPCE = ko.observable();
	self.selectedModule = ko.observable();
	
	$(document).ready( function () {
		// get data from server
		
		// some hard coded data for now...
				
		// get workspace info	
		self.workspaceInfo(new Workspace({'WorkspaceID': 1,
										   'WorkspaceName': 'default',
										   'Description':'My personal workspace'}));
			
		// get PCE list
		self.PCElist.push(new PCE({'ID': 1,
								   'name': 'flux',
								   'description':'cluster',
								   'status':'up',
								   'nodes':4,
								   'corespernode':16,
								   'mempernode':'8GB'}));
				
		self.PCElist.push(new PCE({'ID': 1,
								   'name': 'brie',
								   'description':'LittleFe',
								   'status':'up',
								   'nodes':6,
								   'corespernode':2,
								   'mempernode':'1GB'}));
			
		self.PCElist.push(new PCE({'ID': 3,
								   'name': 'gouda',
								   'description':'LittleFe',
								   'status':'up',
								   'nodes':6,
								   'corespernode':2,
								   'mempernode':'0.5GB'}));
			
		// get job list
		self.Jobslist.push(new Job({'JobID' : 2,
									'Workspace' : 'default',
									'PCE' : 'flux',
									'Module' : 'Hello World',
									'RunName' :'test1',
									'Status' :'Running',
									'Runtime' : '0:00'}));
			
		// get module list
		self.Modulelist.push(new Module({'ID':1,
										 'name':'Hello MPI',
										 'details':'a first parallel program',
										 'formFields':{
											'runname':'',
											'nodes':1,
											'tasks':4}}));
	});
	
	self.welcome1 = self.username + "'s " + self.workspaceInfo().name + " workspace";

	

	// Behaviors
	self.selectPCE = function (PCE) {
		self.selectedPCE(PCE);
		self.selectedModule(null);
	}
	
	self.selectModule = function (m) {
		self.selectedModule(m);
	}
	

	self.changePCE = function () {
		self.selectedPCE(null);
		self.selectedModule(null);
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