const form = document.querySelector('.form');
const feedback = document.querySelector('.formFeedback');

if (form && feedback) {
    form.addEventListener('submit',(ev)=>{
        ev.preventDefault();
        let errors = '';
        if (id_username.value.length<5) {
            errors +=`
                <div class="text text_error">Имя пользователя должно быть не менее 5 символов</div>
            `
        }
        if (id_password.value.length<8) {
            errors +=`
                <div class="text text_error">Пароль должен содержать не менее 8 символов</div>
            `
        }
        if (/^[0-9]+$/.test(id_password.value)) {
            errors +=`
                <div class="text text_error">Введённый пароль состоит только из цифр.</div>
            `
        }
        if (id_password.value !== id_password2.value) {
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