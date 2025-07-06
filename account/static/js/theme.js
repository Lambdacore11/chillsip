let cur_theme = localStorage.getItem('theme') || 'light';

class Theme {
    constructor(tc1,tc2,tc3,bgc1,bgc2,bgc3,bgc4,blc,blch,title){
        this.tc1 = tc1;
        this.tc2 = tc2;
        this.tc3 = tc3;
        this.bgc1 = bgc1;
        this.bgc2 = bgc2;
        this.bgc3 = bgc3;
        this.bgc4 = bgc4;
        this.blc =  blc;
        this.blch = blch
        this.title = title
    }
    set_theme() {

        function set_color(prop,val) {
            document.documentElement.style.setProperty(prop,val);
        }
        
        set_color('--tc1',this.tc1);
        set_color('--tc2',this.tc2);
        set_color('--tc3',this.tc3);
        set_color('--bgc1',this.bgc1);
        set_color('--bgc2',this.bgc2);
        set_color('--bgc3',this.bgc3);
        set_color('--bgc4',this.bgc4);
        set_color('--blc',this.blc);
        set_color('--blch',this.blch);

        cur_theme = this.title;
        localStorage.setItem('theme', this.title);
        const theme_icons = document.querySelectorAll('.themeIcon');
        if (theme_icons.length) {
            theme_icons.forEach(el=>{
                el.src = `${window.STATIC_URL}images/${this.title}.png`;
            })
        }
    } 
}

const light_theme = new Theme (
    '#121212',
    '#FFFFFF',
    '#FF0000',
    '#FFFFFF',
    '#14471E',
    '#68904D',
    '#C8D2D1',
    '#DA6A00',
    '#EE9B01',
    'light',
)

const dark_theme = new Theme (
    '#FFFFFF',
    '#FFFFFF',
    '#CF6679',
    '#1E1E1E',
    '#121212',
    '#121212',
    '#121212',
    '#BB86FC',
    '#03DAC6',
    'dark',
)

document.addEventListener('DOMContentLoaded', () => {
    if (cur_theme === 'light') {
        light_theme.set_theme();
    } else {
        dark_theme.set_theme();
    }
})

const buttons_theme = document.querySelectorAll('.button_theme')
if (buttons_theme.length) {
    buttons_theme.forEach(el=>{
        el.addEventListener('click',(ev)=>{
            ev.preventDefault();
            if(cur_theme === 'light') dark_theme.set_theme();
            else light_theme.set_theme();
        })
    })
}
