define(['knockout'], function (ko) {

    function DropdownViewModel(params) {
        $.ajax({
            url: params.url,
            type: 'GET',
            dataType: 'json',
            data: { id: params.id },
            success: function (response) {
                if (response.status) {
                    this.selectList(response.data);
                } else {
                    this.selectList(["Error"]);
                }
            }
        });
    }

    DropdownViewModel.prototype.select = function (selection) {
        this.selection = selection;
    };

    return DropdownViewModel;

});