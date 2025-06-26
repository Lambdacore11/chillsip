const stars = document.querySelectorAll('.ratingInput__star');

if (stars) {
    stars.forEach(el=>{
        
        el.addEventListener('click',(ev)=>{

            ev.preventDefault();

            const group_number = Number(el.parentElement.dataset['number']);
            const element_number = Number(el.dataset['number']);
            el.nextElementSibling.checked = true;

            stars.forEach(el=>{
                if (Number(el.parentElement.dataset['number']) == group_number && Number(el.dataset['number']) > element_number) {
                    el.src = `${window.STATIC_URL}images/rating/star.png`;
                }
                else if (Number(el.parentElement.dataset['number']) == group_number) {
                    el.src = `${window.STATIC_URL}images/rating/star_selected.png`;
                }
            })   
        
            

        })
    })
}



