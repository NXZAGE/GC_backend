mes.classList.add("now-side_icon");
mes.classList.remove("side_icon");
i = mes.querySelector('.hr').querySelector('.icona');
i.classList.add("now-icona");
i.classList.remove("icona");
window.addEventListener('load', function (){
    messenger_box.scrollTop = messenger_box.scrollHeight;
});