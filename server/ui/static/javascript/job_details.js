function myJob(data){
	var self = this;
	self.jID = data['job_id'];
	self.user = data['user_id'];
	self.ws = data['workspace_id'];
	self.pce = data['pce_id'];
	self.mod = data['module_id'];
	self.name = data['job_name'];
	self.status = data['state'];
	self.time = "0:00";  // not implemented yet
	self.data_files = ko.observableArray(["test.out", "out.txt", "other"]);
	self.output = data['output_file'];
	self.output_str = ko.observable("test");
	self.state_str = data['state_str'];
}

function JobDetailsViewModel() {
	var self = this;

	self.selectedJob = ko.observable();
	self.Jobslist = ko.observableArray();

	self.jobStates = [];

	self.selectedFile = ko.observable("test.txt");
	self.fileOutput = ko.observable();

	self.refreshJobs = function () {
		self.selectedJob(null);
		self.Jobslist.removeAll();

		$.ajax({
		    url:'/public/Jobs/UserJobs/',
		    type:'GET',
		    dataType:'json',
		    success: function(response) {
		        for (var x = 0; x < response.jobs.length; x++){
					var job_data = response.jobs[x];
					self.Jobslist.push(new myJob(job_data));
				}
		    }
		})
    }



	$(document).ready( function () {
	    self.refreshJobs();
	});

	self.selectFile = function () {

		self.selectedFile(this);
	}

	self.selectJob = function (){
	    self.selectedJob(this);
	    $.ajax({
	        url: '/public/Jobs/GetJobInfo/',
	        type:'POST',
	        dataType:'json',
	        data: {'job_id':this.jID},
	        success: function(response) {
	            self.selectedFile(response.file)
	            $("#job_output").text(response.output)
	            self.fileOutput(response.output)
	            this.state_str = response.state;
	        }
	    });

//		$.getJSON(sessionStorage.server + "/jobs/" + this.jID + "?apikey=" + JSON.parse(self.auth_data).apikey,
//			function (data) {
//				this.output = data.jobs.output;
//				this.state_str = data.jobs.state_str;
//			}
//		);
//		$.getJSON(sessionStorage.server + "/jobs/" + this.jID + "/data?apikey=" + JSON.parse(self.auth_data).apikey,
//			function (data) {
//			      console.log(data.jobs);
//			      //this.output_str = data.jobs;
//			      self.selectedJob().output_str(data.jobs);
//			      //self.selectedFile(self.selectedJob().output_str());
//			      self.selectedFile(sessionStorage["server"] + "/../" + self.selectedJob().output_str());
//			}
//		);
	    //self.selectedJob(this);
	}

}

// Activates knockout.js
ko.applyBindings(new JobDetailsViewModel());
