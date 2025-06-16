$(document).ready(function() {

    if (id_street) {

        $('#id_street').select2(

            {language:{noResults: () => "Нет результатов"}},
        );
    }
    
    if (id_is_private && id_apartment) {
    
        id_is_private.addEventListener('click',()=>{

            if (id_is_private.checked) {
                id_apartment.parentElement.style['visibility']='hidden';
            }
            else {
                id_apartment.parentElement.style['visibility']='visible';
            }
        })
    }

    const form = document.querySelector('.form');
    const feedback = document.querySelector('.formFeedback');

    if (form && feedback) {
        form.addEventListener('submit',(ev)=>{
            ev.preventDefault();
            let errors = '';
            if (id_is_private.checked && id_apartment.value) {
                errors +=`
                    <div class="text text_error">Вы указали квартиру при выборе пункта "частный дом"</div>
                `
            }
            else if (!id_is_private.checked && !id_apartment.value) {
                errors +=`
                    <div class="text text_error">Необходимо указать квартиру если не выбран пункт "частный дом"</div>
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
});