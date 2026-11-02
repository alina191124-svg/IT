$(document).ready(function(){
    // Кнопка "Зарегистрироваться"
    $('#67').on('submit',function(e){
        e.preventDefault();
        let err = 0;
        if ($('#fullname').val().trim() === '' || $('#password').val().trim() != $('#confirm_password').val().trim()){
            err = 1;
        }else{
            err = 0;
        }
        if (err == 0){
            $.ajax({
                url: '/user_register',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    name: $('#fullname').val(),
                    password: $('#password').val(),
                    email: $('#username').val()
                }),
                success: function(response){
                    window.location.href = '/login';
                }
            })
        }
    })

    // Кнопка "Войти"
    $('#burmalda').on('submit',function(e){
        e.preventDefault();
        $.ajax({
            url: '/user_authorization',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                password: $('#password').val(),
                email: $('#username').val()
            }),
            success: function(response){
                if (response.result == true){
                    window.location.href = '/profile';
                } else {
                    alert('Неверный логин или пароль!');
                }
            }
        })
    })
})