const form = document.querySelector('.form');
const feedback = document.querySelector('.formFeedback');

if (form && feedback) {
    form.addEventListener('submit',(ev)=>{
        ev.preventDefault();
        let errors = '';
        if (id_username.value.length < 5) {
            errors +=`
                <div class="text text_error">Имя пользователя должно быть не менее 5 символов</div>
            `
        }
        if (!/^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/.test(id_email.value.toLowerCase())) {
            errors +=`
                <div class="text text_error">Введите правильный адрес электронной почты</div>
            `
        }
        if (id_password1.value.length < 8) {
            errors += `
                <div class="text text_error">Пароль должен содержать не менее 8 символов</div>
            `
        }
        if (/^[0-9]+$/.test(id_password1.value)) {
            errors +=`
                <div class="text text_error">Введённый пароль состоит только из цифр.</div>
            `
        }
        if (id_password1.value !== id_password2.value) {
            errors +=`
                <div class="text text_error">Пароли не совпадают</div>
            `
        }
        if (errors === '') {
            form.submit();
        }
        else {
            feedback.innerHTML = errors;
        }
    })
}