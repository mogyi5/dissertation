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


});
