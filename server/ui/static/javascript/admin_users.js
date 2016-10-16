

function UserProfile(data) {
	var self = this;
	self.id = ko.observable(data['user_id']);
	self.username = ko.observable(data['username']);
	self.first_name = ko.observable(data['first_name']);
	self.last_name = ko.observable(data['last_name'])
	self.email = ko.observable(data['email']);
	self.isAdmin = ko.observable(data['is_admin']);
	self.isEnabled = ko.observable(data['is_enabled']);
	self.password = ko.observable('**********'); //fake security

	self.auth_data = sessionStorage['auth_data'];

	self.Workspacelist = ko.observableArray();
	self.Jobslist = ko.observableArray();
	self.PCEslist = ko.observableArray();
	self.Moduleslist = ko.observableArray();

	self.viewUser = function () {
		// go to manage users page and start with this user
		window.location.href = "admin_users.html";
	};

	self.editUser = function () {
		// get all user data

        // get jobs for this user
        $.ajax({
            url: '/admin/Users/Jobs/',
            method: 'POST',
            //headers: {'X-CSRFToken': csrftoken},
            dataType: 'json',
            data: {'user':self.id()},// 'csrfmiddlewaretoken':csrftoken},
            success: function(data) {
                self.Jobslist.removeAll();
                for (var x = 0; x < data.jobs.length; x++){
                    var job = data.jobs[x];
                    self.Jobslist.push(new Job(job, true, false));
                }
            }
        })


		// get workspaces for this user
        $.ajax({
            url: '/admin/Users/Workspaces/',
            method: 'POST',
            dataType: 'json',
            data: {'user':self.id()},// 'csrfmiddlewaretoken':csrftoken},
            success: function (data) {
                self.Workspacelist.removeAll();
                for (var x = 0; x < data.workspaces.length; x++){
                    var ws = data.workspaces[x];
                    self.Workspacelist.push(new Workspace(ws, true));
                }
            }
        })
	};

    self.updateUser = function() {
        var data = {
            'username':this.username(),
            'password':this.password(),
            'is_admin':this.isAdmin(),
            'is_enabled':this.isEnabled(),
            'email':this.email(),
            'first_name':this.first_name(),
            'last_name':this.last_name(),
            'user_id':this.id()
        }
        if (this.id() == undefined) {
            var url = '/admin/Users/Create/';
        } else {
            var url = '/admin/Users/Update/'
        }
        $.ajax({
            url: url,
            type: 'POST',
            dataType: 'json',
            data: data,
            success: function(result) {
                if (result['status'] == 1) {
                    // This means it was successful
                } else {
                    // unsuccesful
                    alert(result['status_message'])
                }
            }
        })
    };


	self.removeFromWorkspace = function () {
		// this is the workspace object
		self.Workspacelist.remove(this);
		alert("removing " + self.username() + " from workspace " + this.name);
	}

	self.removeOnServer = function () {
		// For now it just disables the user not deletes them
		//var remove = confirm("Remove " + self.username() + " from the server?");

		// For now just make request to update user and set is_enabled to false
		$.ajax({
      		type: 'POST',
      		url: '/admin/Users/Disable/',
      		data: {'user_id':this.id()},
      		dataType: 'json',
      		success: function(response) {
      		    if (response['status'] == -1) {
      		        // this means it failed
      		        alert(response['status_message'])
      		    }
      		}

	  	} );
		this.isEnabled(false);
	  

	}

}



function AdminUserViewModel() {
    var self = this;
    self.username = sessionStorage['UserID'];
    self.userID = sessionStorage['UserID'];
    self.auth_data = sessionStorage['auth_data'];

    self.selectedUser = ko.observable();

    self.Userslist = ko.observableArray();

    self.changeUser = function () {
        self.selectedUser(null);
    };

    self.selectUser = function () {
        self.selectedUser(this);
        this.editUser();
    }

    self.deleteUser = function () {
        // tell server to delete this user
        //self.Userslist.remove(this);
        if (self.selectedUser() == this) {
            self.selectedUser(null);
        }
        this.removeOnServer();
    }

    self.addUser = function () {
        // need to get user ID from the server, maybe not until data is populated?
        var newUser = new UserProfile({'id':-1, 'username': 'username', 'full_name' : 'fullName', 'email':'email', 'isAdmin': false});
        self.Userslist.push(newUser);
        self.selectedUser(newUser);
    }

    $(document).ready( function () {
        // reinitialize values
        self.Userslist([]);
        // Get all users from server
        $.ajax({
            url: '/admin/Users/GetAll/',
            type: 'GET',
            dataType:'json',
            success: function(data) {
                for (var x = 0; x < data.users.length; x++){
                    var user_data = data.users[x];
                    self.Userslist.push(new UserProfile(user_data));
                }
            }
        })
    });
}

// Activates knockout.js
ko.applyBindings(new AdminUserViewModel());
