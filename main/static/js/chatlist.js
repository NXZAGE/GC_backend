mes.classList.add("now-side_icon");
mes.classList.remove("side_icon");
i = mes.querySelector('.hr').querySelector('.icona');
i.classList.add("now-icona");
i.classList.remove("icona");
window.addEventListener('load', function (){
for(let i = 0; i < last_message.length; i++){
if(last_message[i].innerHTML.length >= 40){
last_message[i].innerHTML = last_message[i].innerHTML.slice(0, 40) + "...";
}
}
});