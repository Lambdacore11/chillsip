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
});