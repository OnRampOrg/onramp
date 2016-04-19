// This should be replaced by something actually secure at somepoint.

// This is a simple *viewmodel* - JavaScript that defines the data and behavior of your UI
function DummyLoginViewModel() {
    var self = this;
    self.username = ko.observable("");
    self.password = ko.observable("");
    sessionStorage["UserID"] = -999;
    sessionStorage["isAdmin"] = false;
    // find a better way to do this!!
    sessionStorage["server"] = "http://flux.cs.uwlax.edu/~ssfoley/server/api";
    
    self.welcome = ko.computed( function() { return "Welcome " + self.username + "!";});
    
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
	    var rt = JSON.parse(data.responseText);
	    sessionStorage["UserID"] = rt.auth.user_id;
	    sessionStorage["apikey"] = rt.auth.apikey;
	    sessionStorage["auth_data"] = JSON.stringify(rt.auth);
	    // check if admin
	    //FIXME!!!!!
	    if(rt.auth.username == "admin"){
		window.location.href = "admin_dashboard.html";
	    }
	    else {
		window.location.href = "user_dashboard.html";
	    }

	    
	}
	else if(data.status == 401){
	    alert("Incorrect login info.  Please try again, or contact the admin to create or reset your account.");
	}
	else {
	    alert("Something went wrong with the sending or receiving of the ajax call.  Status code: " + data.status);
	}
	
    };
    
    self.error_func = function( jqXHR, textStatus, errorThrown) {
	console.log("error: " + textStatus);
	console.log("error: " + errorThrown);
    };
    
    self.dummyValidate = function() {
	// do REST call
	//var data = {"password":this.password(), "username":this.username()};
	
	//$.ajax({contentType:"application/json", url: 'http://flux.cs.uwlax.edu/onramp/api/login'});
	console.log("before ajax...");
	/*
	  var results = $.ajax({
	  type: 'POST',
	  url:
	  dataType: 'application/json',
	  
	  data: ,
	  success:
	  contentType: "application/json"
	  //contentType: 'application/json'
	  //error: function (xhr, ajaxOptions, thrownError) {
	  //alert(xhr.status);
	  //alert(thrownError);
	  //}
	  });
	*/
	$.ajax({
		type: 'POST',
		    url: sessionStorage["server"] + "/login",
		    data: JSON.stringify({'password':self.password(), 'username':self.username()}),
		    complete: self.complete_func,
		    dataType: 'application/json',
		    contentType: 'application/json'
		    } );
	
	console.log("after ajax...");
    };
    
    self.logout = function (){
	// send post to server
	$.ajax({
		type: 'POST',
		url: sessionStorage["server"] + 'logout',
		data: self.auth_data,
		complete: function () {
		    window.location.href = "start.html";
		},
		dataType: 'application/json',
		contentType: 'application/json'
	    } );
	
    };
    
    
}

// Activates knockout.js
ko.applyBindings(new DummyLoginViewModel());
