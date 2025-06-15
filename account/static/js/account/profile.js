const form = document.querySelector('.form');
const feedback = document.querySelector('.formFeedback');

if (form && feedback) {
    form.addEventListener('submit',(ev)=>{
        ev.preventDefault();
        let errors = '';
        if (!/^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/.test(id_email.value.toLowerCase())) {
            errors +=`
                <div class="text text_error">Введите правильный адрес электронной почты</div>
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