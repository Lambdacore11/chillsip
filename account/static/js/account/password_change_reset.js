const form = document.querySelector('.form');
const feedback = document.querySelector('.formFeedback');

if (form && feedback) {
    form.addEventListener('submit',(ev)=>{
        ev.preventDefault();
        let errors = '';
        if (id_new_password1.value.length<8) {
            errors +=`
                <div class="text text_error">Пароль должен содержать не менее 8 символов</div>
            `
        }
        if (/^[0-9]+$/.test(id_new_password1.value)) {
            errors +=`
                <div class="text text_error">Введённый пароль состоит только из цифр.</div>
            `
        }
        if (id_new_password1.value !== id_new_password2.value ) {
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