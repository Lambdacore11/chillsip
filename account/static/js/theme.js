window.addEventListener('DOMContentLoaded', () => {
    const isDark = document.documentElement.classList.contains('dark');
    const themeIcons = document.querySelectorAll('.themeIcon');

    if (themeIcons.length > 0) {
        themeIcons.forEach(el => {
            el.src = `${window.STATIC_URL}images/${isDark ? 'dark' : 'light'}.png`;
        });
    }
    document.body.classList.add('ready');
});

const buttons_theme = document.querySelectorAll('.button_theme');
if (buttons_theme.length) {
    buttons_theme.forEach(el=>{
        el.addEventListener('click',(ev)=>{
            ev.preventDefault();
            const isDark = document.documentElement.classList.toggle('dark');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            const theme_icons = document.querySelectorAll('.themeIcon');
            if (theme_icons.length) {
                theme_icons.forEach(el=>{
                    el.src = `${window.STATIC_URL}images/${isDark ? 'dark' : 'light'}.png`;
                }) 
            }  
        })
    })
}
