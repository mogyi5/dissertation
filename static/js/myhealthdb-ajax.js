$(document).ready(function () {
    // task complete
    $('.complete').click(function () {
        var task = $(this)
        var par = $(this).parent()
        $.ajax({
            type: "POST",
            data: {
                'id': task.attr('name'),
                'csrfmiddlewaretoken': window.CSRF_TOKEN
            },
            url: task.data('url'),
            dataType: "json",
            success: function (response) {
                par.fadeOut(200, function () {
                    par.remove();
                });
                // alert(response.message);
                // alert('Company likes count is now ' + response.likes_count);
            },
            error: function (rs, e) {
                alert(rs.responseText);
            }
        });
    });

    // medication is done
    $('.done').click(function () {
        var medication = $(this)
        //     var par = $(this).parent()
        $.ajax({
            type: "POST",
            data: {
                'id': medication.attr('name'),
                'csrfmiddlewaretoken': window.CSRF_TOKEN
            },
            url: medication.data('url'),
            dataType: "json",
            success: function (response) {
                // par.fadeOut(200, function(){
                //     par.remove();
                // });
                alert(response.message);
                //             // alert('Company likes count is now ' + response.likes_count);
            },
            error: function (rs, e) {
                alert(rs.responseText);
            }
        });
    });

    function confirmRegistration() {
        return confirm("Are you sure you want to register with this practice? Your medical data will be shared.");
    }

    // medication is done
    $('.register').click(function () {

        if(!confirmRegistration()) {
            return false;
        }

            var register = $(this)
        //     var par = $(this).parent()

            $.ajax({
                type: "POST",
                data: {
                    'id': register.attr('name'),
                    'csrfmiddlewaretoken': window.CSRF_TOKEN
                },
                url: register.data('url'),
                dataType: "json",
                // beforeSend: function () {
                //     return confirm("Are you sure?");
                // },
                success: function (response) {
                    // par.fadeOut(200, function(){
                    //     par.remove();
                    // });
                    alert(response.message);
                    //             // alert('Company likes count is now ' + response.likes_count);
                },
                error: function (rs, e) {
                    alert(rs.responseText);
                }
            });
        
    });

    function confirmConfirmation() {
        return confirm("Are you sure you want to register this patient?");
    }


    // medication is done
    $('.register_pat').click(function () {

        if(!confirmConfirmation()) {
            return false;
        }

        var register_pat = $(this);
        var par = $(this).parent();

        $.ajax({
            type: "POST",
            data: {
                'id': register_pat.attr('name'),
                'csrfmiddlewaretoken': window.CSRF_TOKEN
            },
            url: register_pat.data('url'),
            dataType: "json",
            success: function (response) {
                par.fadeOut(200, function(){
                    par.remove();
                });
                alert(response.message);
            },
            error: function (rs, e) {
                alert(rs.responseText);
            }
        });

    });

    function confirmRejection() {
        return confirm("Are you sure you want to reject this patient?");
    }


        // medication is done
        $('.reject_pat').click(function (event) {

            if(!confirmRejection()) {
                return false;
            }

            var reject_pat = $(this);
            var par = $(this).parent();
    
            $.ajax({
                type: "POST",
                data: {
                    'id': reject_pat.attr('name'),
                    'csrfmiddlewaretoken': window.CSRF_TOKEN
                },
                url: reject_pat.data('url'),
                dataType: "json",
                success: function (response) {
                    par.fadeOut(200, function(){
                        par.remove();
                    });
                    alert(response.message);
                },
                error: function (rs, e) {
                    alert(rs.responseText);
                }
            });
    
        });


});
