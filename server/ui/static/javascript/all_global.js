function PCE(data, view){
	var self = this;
	self.id = data['pce_id'];
	self.name = data['pce_name'];
	self.status = data['state'];
	//self.nodes = data['nodes'];
	//self.corespernode = data['corespernode'];
	//self.mempernode = data['mempernode'];
	
	// CHANGE BE BACK AFTER TESTING
	//self.description = data['description'];
	// hard-coded version for testing the system
	self.description = "This machine is a generic cluster with four nodes, one serves as the head node, and the other three are compute nodes.  Each compute node has 8 cores and 48GB of memory.";
	self.url = "http://flux.cs.uwlax.edu/";
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
	self.jID = data['job_id'];
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
	self.wID = data['workspace_id'];
	self.name = data['workspace_name'];
	self.desc = data['description'];


	self.captureWSID = function() {
		sessionStorage.setItem("WorkspaceID", this.id);
		//alert("workspace " + localStorage.getItem('WorkspaceID'));
        window.location.href = "/public/Workspace";
		
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
        type: 'GET',
	    url: '/logout/',
	    success: function() {
	        window.location = "/"
	    }
	} );

}


/*
    The below code ensures we send our CSRF token that we got from django
    on every ajax request. We do this so Django knows where the request is
    coming from and that it is not a CSRF attack
*/
$(document).ajaxSend(function(event, xhr, settings) {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    function sameOrigin(url) {
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }
    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
});


