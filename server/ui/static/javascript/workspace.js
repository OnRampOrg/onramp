
// Select all elements with data-toggle="tooltips" in the document
$('[data-toggle="tooltip"]').tooltip();
$('.collapse').collapse();
var module_name = "";
//var user_design_split = sessionStorage.Username.split("");
//var user_design = user_design_split[0];
//console.log("CHRISTA user_design: "+ user_design);


function workspaceModule(data){
	var self = this;
	self.id = data['module_id'];
	self.name = data['module_name'];
	self.desc = data['description'];
	self.path = data['src_location'];
	self.formFields = ko.observableArray();
	self.PCEs = ko.observableArray();
	self.formInfo = ko.observableArray();

	self.addDefaultFormFields = function () {
		this.formFields.push({"field": "name", "value": "test"});
		this.formFields.push({"field": "nodes", "value": 1});
		this.formFields.push({"field": "processes", "value": 4});
	}

	self.getRealFormFields = function (pce_id) {
		var module_index = /[^/]*$/.exec(self.path)[0];
		self.formFields.removeAll();
		$.ajax({
		    url:'/public/Workspace/GetModuleOptions/',
		    type:'POST',
		    dataType:'json',
		    data: {'pce_id':pce_id, 'module_id':self.id},
		    success: function(response) {
				var module_index = /[^/]*$/.exec(self.path)[0];

                self.formFields.push({field:"job_name", data:""});
				response.uioptions.onramp.forEach(function (item, index, array){
					self.formFields.push({field:"onramp " + item, data:""});
					self.formInfo.push({formid: item});
				});

				if(module_index == "mpi-ring"){
					response.uioptions["ring"].forEach(function (item, index, array){
						module_name = "ring";
						self.formFields.push({field:"ring " + item, data:""});
						self.formInfo.push({formid: item});
						console.log("christa"+ item);
					});
				}
				else if(module_index == "template"){
					response.uioptions["hello"].forEach(function (item, index, array){
						module_name = "hello";
						self.formFields.push({field:"hello " + item, data:""});
						self.formInfo.push({formid: item});
						console.log("christa"+ item);
					});
				}
				else {
					response.uioptions[module_index].forEach(function (item, index, array){
						module_name = self.name;
						self.formFields.push({field:self.name + " " + item, data:""});
						self.formInfo.push({formid: item});
						console.log("christa"+ item);
					});
				}

				console.log("added fields!");
				console.log(self.formFields());
				//call method to set the ids of each label
				setFormId(self.formInfo());
		    }
		})
	}
}

//forEach(<instance> in <objects>)
var setFormId = function(formInfo){
	var formID = "";
	var labels = document.getElementsByTagName("label");
		for(var i = 1; i < labels.length; i++){
			formID = formInfo[i-1].formid;
			labels[i].setAttribute("id", formID);
			var myDescription = getDescription(formID);
	
			
			//<span id="helpBlock" class="help-block">A block of help text that breaks onto a new line and may extend beyond one line.</span>
			if( myDescription !== "none"){
				if(sessionStorage.Username === "q" || sessionStorage.Username === "Q"){
					var div = document.createElement("div");
					div.setAttribute("class", "formTip notActive");
					var myDescription = getDescription(formID);
					var description = document.createTextNode(myDescription);
					div.appendChild(description);
					$(div).insertAfter(labels[i]);
					
				}
				else{ //busy design
					var myDescription = getDescription(formID);
					$(labels[i]).append("<span style = \"display:block;font-size:80%\" class = \"help-block\"><span class = \"glyphicon glyphicon-info-sign\"></span> "+myDescription+"</span>");
				} 
			}
			
			if(sessionStorage.Username === "q" || sessionStorage.Username === "Q"){
				//check for form label click
				$(document).ready(function () {
					$('.formLabel').click(function(e) {
						var id = $(e.target).attr("id");
						var self = e.target;
						console.log("myid: "+id);
					$(".formTip").removeClass("isActive"); 
					$(".formTip").addClass("notActive");
					$(self).next().removeClass('notActive');
						
					$(self).next().addClass('isActive');
					
					});
				});
				//check for white space click
				$(document).mouseup(function (e){
					var container = $(".formLabel");

					if (!container.is(e.target) // if the target of the click isn't the container...
						&& container.has(e.target).length === 0) // ... nor a descendant of the container
					{
						$(".formTip").removeClass("isActive"); 
						$(".formTip").addClass("notActive");
					}
				});
			}

		}
}

	
/*maybe put in placeholder for the default*/

var getDescription = function( formID ){
	
	var description = "";
	if(formID === "rectangles"){
		description = "Number of rectangles for the Riemann Sum. Default = 100000000";
	}
	else if(formID === "threads"){
		if(module_name == "monte_carlo"){
			description = "Select how many threads to use in the parallel version. Default = 1, max = 32.";
		}
		else if(module_name == "AUC"){
			description = "Number of OpenMP threads to use for each process. Default = 1";
		}
	}
	else if(formID === "mode"){
		if(module_name == "monte_carlo"){
			description = "Which program and version to run: 1s coin_flip sequential, 1p coin_flip parallel, 2s draw_four_suits sequential, 2p draw_four_suits parallel, 3s roulette_sim sequential, 3p roulette_sim parallel. Default = 1s"
		}
		else if(module_name == "AUC"){
			description = "Version of program to run ('s' -> serial, 'o' -> openmp, 'm' -> mpi, 'h' -> hybrid). Default = s";
		}
	}
	else if(formID === "np"){
		if(module_name == "monte_carlo"){
			description = "Number of processes (ignored for Monte Carlo)";
		}
		else{
			description = "Number of processes";
		}
	}
	else if(formID === "nodes"){
		if(module_name == "monte_carlo"){
			description = "Number of nodes (ignored for Monte Carlo)";
		}
		else{
			description = "Number of nodes";
		}
	}
	else if(formID === "name"){
		description = "Specify a name"
	}
	else if(formID === "pi_trials"){
		description = "Number of trials for the pi simulation. Default= 100000000, max = 32";
	}
	else{
		description = "none";
	}
	return description;
}
var openModuleModal = function(){
	$('#moduleModal').modal('show');
}

var openPCEModal = function(){
	$('#PCEModal').modal('show');
}


//forEach(instance in objects)
var displayConcepts = function(btn){
	
	var childClass = $(btn).next().className;
	console.log("christa childClass = " + childClass);
	
	//because of the button calling this method you can't click the button to make the concepts div disapper because it will hit the below two lines
	$(".info-div").removeClass("info-notActive"); //make 
	$(".info-div").addClass("info-isActive");
		
	//check for white space click
	$(document).mouseup(function (e){
		var container = $(".info-div");

		if (!container.is(e.target) // if the target of the click isn't the container...
			) // ... nor a descendant of the container
		{
			$(".info-div").removeClass("info-isActive"); //make 
			$(".info-div").addClass("info-notActive");
		}
	});

}


function myWorkspace(data){
	var self = this;
	self.id = data['workspace_id'];
	self.name = data['workspace_name'];
	//self.desc = data['description'];
	// hard-coded description of a workspace, this is really just the info for the pi module.
	self.desc = "This workspace is for exploring parallelism and scaling using some embarassingly parallel applications.  The workspace contains the template module which runs an MPI version of \"Hello world!,\" the Monte Carlo module which includes several programs that use a Monte Carlo approach for simulating random events, and the AUC module which uses Riemann sums to estimate pi.";
	console.log("CHRISTA DESC: " + self.desc);

	self.captureWSID = function () {

		localStorage.setItem("WorkspaceID", self.id);
		alert("workspa e " + localStorage.getItem('WorkspaceID'));
		if(sessionStorage.Username === "q" || sessionStorage.Username === "Q"){
			window.location.href = "workspace_quiet.html";
		}
		else{
			window.location.href = "workspace.html";
		}
		return;
	}
}


function OnrampWorkspaceViewModel () {
	// Data
	var self = this;
	self.userID = sessionStorage['UserID'];
	self.auth_data = sessionStorage['auth_data'];
	self.workspaceID = sessionStorage['WorkspaceID'];
	self.workspaceInfo = ko.observable();
	//self.workspaceInfo(new Workspace({'WorkspaceID': 1,
	//'WorkspaceName': 'default',
	//'Description':'My personal workspace'}));

//	self.username = JSON.parse(self.auth_data).username;

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
		$.ajax({
		    url: '/public/Workspace/GetWorkspace/',
            type: 'POST',
            dataType:'json',
            data: {'workspace_id':self.workspaceID},
            success: function(response) {
                if (response.success) {
                    self.welcome1("Workspace: "+response.data['workspace_name'])
                    self.workspaceInfo(new myWorkspace(response.data))
                } else {
                    alert(response.status_message);
                }
            }
		})

        $.ajax({
            url: '/public/Workspace/GetPCEs/',
            type: 'POST',
            dataType: 'json',
            data: {'workspace_id':self.workspaceID},
            success: function (response) {
                if (response.success) {
                    for (var i=0; i<response.pces.length; i++) {
                        var newpce = new PCE(response.pces[i]);
                        self.PCElist.push(newpce);
                        self.allPCEs.push(newpce);
                    }
                } else {
                    alert(response.status_message);
                }
            }
        })
	});

	// Behaviors
	self.selectPCE = function (PCE) {
		self.selectedPCE(PCE);
		$.ajax({
		    url: '/public/Workspace/GetModules/',
		    type:'POST',
		    dataType:'json',
		    data: {'workspace_id':self.workspaceID, 'pce_id':PCE.id},
		    success: function(response) {
		        if (response.success) {
		            $("#module-select-header").text("Now select a module to run")
		            for (var i=0; i<response.modules.length; i++) {
		                var newmod = new workspaceModule(response.modules[i]);
		                self.Modulelist.push(newmod);
		            }
		        } else {
		            alert(response.status_message);
		        }
		    }
		})
	}

	self.selectModule = function (m) {
		self.selectedModule(m);
		m.getRealFormFields(self.selectedPCE().id);
		/*add module descriptions here because we need the module to be selected
		 above or the html will not exist */
		if(self.selectedModule().name == "monte_carlo"){
			document.getElementById("module-desc").innerHTML = "Monte Carlo methods are a class of computational algorithms that use repeated random sampling to obtain numerical results. Typically, a single workhorse for-loop is used to generate the repeated and independent simulations. Monte Carlo methods are often employed when there is not a closed form or deterministic solution to the underlying problem. As this sort of problem is quite common, Monte Carlo methods are used in a wide variety of fields from computational chemistry to finance. While these topics are important, you may be more interested in the more intriguing application of Monte Carlo methods to gambling and card games. The well known games of roulette and poker will both be used as the basis for the exercises in this module. Upon completion of this module, students should be able to: 1) Identify embarrassingly parallel problems 2.) Understand the real-life applications of stochastic methods 3.) Measure the scalability of a parallel application.";
		}
		if(self.selectedModule().name == "AUC"){
			document.getElementById("module-desc").innerHTML = "This module introduces a method to approximate the area under a curve using a Riemann sum. Serial and parallel algorithms addressing shared and distributed memory concepts are discussed, as well as the MapReduce algorithm classification. A method to estimate pi (&#x3C0) is also developed to demonstrate an example scientific application. Exercises focus on how to measure the performance and scaling of a parallel application in multi-core and many-core environments. Upon completion of this module, students should be able to: 1) Understand the importance of approximating the area under a curve in modeling scientific problems, 2) Understand and apply parallel concepts, 3) Measure the scalability of a parallel application over multiple or many cores, and 4) Identify and explain the Area Under a Curve algorithm using the Berkeley Dwarfs system of classification.";
		}
		if(self.selectedModule().name == "template"){
			document.getElementById("module-desc").innerHTML = "This module prints out a greeting to the name you give it as well as which process it was executed on!";
		}
	}


	self.changePCE = function () {
		// display all PCEs
		self.PCElist.removeAll();
        // un-select any selected module
        self.selectedModule(null);
        console.log("Changing PCE, selected module is null");
        self.Modulelist.removeAll();
        for(var i = 0; i < self.allPCEs.length; i++){
            self.PCElist.push(self.allPCEs[i]);
        }
        for(var i = 0; i < self.allModules.length; i++){
            console.log("adding module " + self.allModules[i] + " to the list");
            self.Modulelist.push(self.allModules[i]);
        }
        // unselect the selected pce
		self.selectedPCE(null);
	}

	self.changeModule = function () {
	    // un-select the current module
		self.selectedModule(null);
	}


	this.launchJob = function(formData){
		console.log("launching job");
		// construct uioptions
		var opts = {"onramp":{}};
		var mod_name = self.selectedModule().name;
		if(self.selectedModule().name == "mpi-ring"){
			mod_name = "ring";
		}
		else if (self.selectedModule().name == "template"){
			mod_name = "hello";
		}
		opts[mod_name] = {};
		formData.formFields().forEach( function(item, index, array){
			
			if(item.field != "job_name"){
				if(item.field.search("onramp") >= 0){
					// get onramp fields
					console.log(item.field.slice(7));
					opts["onramp"][item.field.slice(7)] = item.data;
				}
				else if(item.field.search(mod_name) >= 0){
					console.log(item.field.slice("CHRISTA: "+mod_name.length + 1));
					opts[mod_name][item.field.slice(mod_name.length + 1)] = item.data;
				}
				else {
					console.log("badness!!!");
				}
			}
			else {
				console.log(index + ") " + item.field + " : " + item.data);
			}
		});
		console.log(formData.formFields()[0].data);
		

		var data_packet = {
            "workspace_id": parseInt(self.workspaceID),
            "module_id" : self.selectedModule().id,
            "pce_id" : self.selectedPCE().id,
            "job_name" : formData.formFields()[0].data,
			"uioptions" : JSON.stringify(opts)
		};

		// POST to jobs
		$.ajax({
			type: "POST",
			url: '/public/Workspace/LaunchJob/',
			type:'POST',
			dataType:'json',
			data: data_packet,
			success: function (response){
				// create confirm with job id info
				if(response.status){
					if(window.confirm("Job created.  ID " + response.job_id + "\nClick OK to view job results page.  Cancel to stay on this page.")){
						window.location.href = "/public/Jobs";
					}
					// else do nothing
				}
				else{
					alert("Something went wrong when connecting to the server.  Status code: " + data.status);
				}
			}
		});

	}


// helper functions
self.findById = function (thisList, id){
	for(var i = 0; i < thisList.length; i++){
		if(thisList[i].id == id){
			return thisList[i];

		}
	}
	return null;
}



}


ko.applyBindings(new OnrampWorkspaceViewModel());

