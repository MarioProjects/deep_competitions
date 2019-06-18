$(document).ready(function () {

    // Esa funcion se dispara al click sobre los items del dropdown selector de base de datos
    $(".dropdown-item").click(function(){
        $db_selected = $(this).text();
        $previous_db = $(this).parents(".dropdown").find('.btn').text().replace(/\s/g, '');
        // Debemos comprobar si la base de datos seleccionada es la que ya estaba -> No hacemos nada o recargamos?!
        $(this).parents(".dropdown").find('.btn').html($db_selected + ' <span class="caret"></span>');
      });

    $("#btnRegister").click(function(){
        $('#registerModal').modal('show');
    });

    $("#btnLogin").click(function(){
        $('#loginModal').modal('show');
    });

    $("#btnLogout").click(function(){
        window.location.href = '/logout'; //relative to domain
    });

    $("#submit-btn-mnist").click(function(){
        $('#mnistSubmitModal').modal('show');
    });

    $("#submit-btn-cifar10").click(function(){
        $('#cifar10SubmitModal').modal('show');
    });

});

function db_info(data, table, username){
    if(jQuery.isEmptyObject(data) || data == ""){
        var newRowContent = "<tr class='empty_table'><th scope='row'>#</th><td>There are no Submissions</td> <td> </td><td> </td><td> </td></tr>";
        table.find("tbody").append(newRowContent);
    }else{
        $count = 1;
        jQuery.each(data, function(i, val) {
            // data -> name, score, entries, utc
            console.log(val[0]);
            $name = val[0];
            $score = val[1];
            $entries = val[2];
            $utc = val[3];
            if($name==username){
                var newRowContent = "<tr class='my_submission'><th scope='row'>"+$count+"</th><td>"+$name+"</td><td>"+$score+"</td><td>"+$entries+"</td><td>"+$utc+"</td></tr>";
            }else{
                var newRowContent = "<tr><th scope='row'>"+$count+"</th><td>"+$name+"</td><td>"+$score+"</td><td>"+$entries+"</td><td>"+$utc+"</td></tr>";
            }
            table.find("tbody").append(newRowContent);
            $count+=1;
        });
    }
}

function manage_modals(modal){
    if(modal.modal_type=="register_ok"){
        $('#okRegisterModal').modal('show');
    }else if(modal.modal_type=="register_error"){
        $('#wrongRegisterModal').modal('show');
    }else if(modal.modal_type=="login_ok"){
        $('#okLoginModal').modal('show');
    }else if(modal.modal_type=="login_error"){
        $('#wrongLoginModal').modal('show');
    }else if(modal.modal_type=="logout_ok"){
        $('#okLogoutModal').modal('show');
    }else if(modal.modal_type=="wrong_extension"){
        $('#wrongExtensionModal').modal('show');
    }else if(modal.modal_type=="submission_without_username"){
        $('#noUserSubmissionnModal').modal('show');
    }else if(modal.modal_type=="submission_ok_lower"){
        $('#lowerSubmissionModal').modal('show');
    }else if(modal.modal_type=="submission_ok_higher"){
        $('#higherSubmissionModal').modal('show');
    }
}