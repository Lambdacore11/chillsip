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
                const popup = document.querySelector('.popup')
                const popup_text = document.querySelector('.popup__text')
                const yes = document.querySelector('#yes')
                const no = document.querySelector('#no')
                if (popup && popup_text && yes && no) {
                    popup.classList.add('active')
                    popup_text.textContent = `Улица: ${id_street.options[id_street.selectedIndex].text}\n\nДом: ${id_building.value}`
                    if (id_apartment.value) {
                        popup_text.textContent +=`\n\nКвартира: ${id_apartment.value}`
                    }
                    popup_text.textContent += '\n\n\nвсе верно?'
                    yes.addEventListener('click',()=>{
                        form.submit()
                    })
                    no.addEventListener('click',()=>{
                        popup.classList.remove('active')
                        console.log('sefsef');
                        
                    })
                }
                
            }
            else {
                feedback.innerHTML = errors;
            }
        })
    }

    const incrementCartItem = document.querySelectorAll('.incrementCartItem');
    const decrementCartItem = document.querySelectorAll('.decrementCartItem');
    const cartTotalPrice = document.querySelector('#cartTotalPrice');

    if (incrementCartItem.length && cartTotalPrice ) {
        incrementCartItem.forEach(el=>{
            el.addEventListener('click', (e) =>{
                e.preventDefault()
                const url = el.dataset['url']
                fetch(url,   
                    {
                        method:'GET',
                        headers:{
                        'X-Requested-With': 'XMLHttpRequest', 
                        }
                    }
                )
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const cartItemCount = document.querySelector(`#cartItemCount${el.dataset['id']}`);
                        const cartItemPrice = document.querySelector(`#cartItemPrice${el.dataset['id']}`);
                        const cartItemTotalPrice = document.querySelector(`#cartItemTotalPrice${el.dataset['id']}`);

                        if (cartItemCount && cartItemPrice && cartItemTotalPrice) {
                            cartItemCount.textContent =  data.new_count;
                            cartItemTotalPrice.textContent = ((parseFloat(cartItemTotalPrice.textContent.replace(',','.')) + parseFloat(cartItemPrice.textContent.replace(',','.'))).toFixed(2) + '₽').replace('.',',');
                            cartTotalPrice.textContent = ((parseFloat(cartTotalPrice.textContent.replace(',','.')) + parseFloat(cartItemPrice.textContent.replace(',','.'))).toFixed(2) + '₽').replace('.',',');
                        }
                    }
                    
                })
                .catch(error =>{
                    console.error('Error:',error)
                })
            })
        })
        
    }

    if (decrementCartItem.length && cartTotalPrice ) {
        decrementCartItem.forEach(el=>{
            el.addEventListener('click', (e) =>{
                e.preventDefault()
                const url = el.dataset['url']
                fetch(url,   
                    {
                        method:'GET',
                        headers:{
                        'X-Requested-With': 'XMLHttpRequest', 
                        }
                    }
                )
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const cartItemCount = document.querySelector(`#cartItemCount${el.dataset['id']}`);
                        const cartItemPrice = document.querySelector(`#cartItemPrice${el.dataset['id']}`);
                        const cartItemTotalPrice = document.querySelector(`#cartItemTotalPrice${el.dataset['id']}`);

                        if (cartItemCount && cartItemPrice && cartItemTotalPrice) {
                            cartItemCount.textContent =  data.new_count;
                            cartItemTotalPrice.textContent = ((parseFloat(cartItemTotalPrice.textContent.replace(',','.')) - parseFloat(cartItemPrice.textContent.replace(',','.'))).toFixed(2) + '₽').replace('.',',');
                            cartTotalPrice.textContent = ((parseFloat(cartTotalPrice.textContent.replace(',','.')) - parseFloat(cartItemPrice.textContent.replace(',','.'))).toFixed(2).replace('.',',') + '₽').replace('.',',');
                        }
                    }
                    
                })
                .catch(error =>{
                    console.error('Error:',error)
                })
            })
        })
        
    }

});