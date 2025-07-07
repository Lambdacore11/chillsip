const ac_title = document.querySelectorAll('.accordeon__title');
const ac_content = document.querySelectorAll('.accordeon__content');

if (ac_title && ac_content) {
    ac_title.forEach(title =>{
        title.addEventListener('mouseover',() =>{
            ac_content.forEach(cont => {
                if (title.dataset['id'] === cont.dataset['id']) {
                    cont.style['display'] = 'block';
                }
            })
        })

    })
    ac_title.forEach(title =>{
        title.addEventListener('mouseout',() =>{
            ac_content.forEach(cont => {  
                cont.style['display'] = 'none';
            })
        })

    })
}