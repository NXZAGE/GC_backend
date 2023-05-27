let dt = new DataTransfer();

mes.classList.add("now-side_icon");
mes.classList.remove("side_icon");
i = mes.querySelector('.hr').querySelector('.icona');
i.classList.add("now-icona");
i.classList.remove("icona");

var background = document.getElementById("box-img")

$('.input-file input[type=file]').on('change', function(){
	let $files_list = $(this).closest('.input-file').next();
	$files_list.empty();
	for(let i = 0; i < 1; i++){
		let file = this.files.item(i);
		dt.items.add(file);
		let reader = new FileReader();
		reader.readAsDataURL(file);
		reader.onloadend = function(){
			let new_file_input = '<div class="input-file-list-item">' +
				'<img class="input-file-list-img" src="' + reader.result + '">' +
				'<a href="#" onclick="removeFilesItem(this); return false;" class="input-file-list-remove">x</a>' +
			'</div>';
			$files_list.append(new_file_input);
		}
		let name_avatar = document.getElementsByClassName("displayed_info");
        name_avatar[0].innerText = file.name;
	    console.log(dt.files)
	};
	this.files = dt.files;
	let btn = document.getElementById("add_btn");
	btn.style.visibility = "hidden";
	btn.style.width = '0';
	btn.style.height = '0';
	btn.style.margin = '0';
	document.getElementById("input-list").style.margin = "0 auto";
});

function removeFilesItem(target){
    let name_avatar = document.getElementsByClassName("displayed_info");
    name_avatar[0].innerText = "None Image";
	let name = $(target).prev().text();
	let input = $(target).closest('.input-file-row').find('input[type=file]');
	$(target).closest('.input-file-list-item').remove();
	for(let i = 0; i < dt.items.length; i++){
		if(name === dt.items[i].getAsFile().name){
			dt.items.remove(i);
		}
	}
	input[0].files = dt.files;
	document.getElementById('add_btn').removeAttribute("style");
	document.getElementById("input-list").removeAttribute("style");
	if(document.getElementById("is_del")){
        is_del.value = "1"
    }
	dt = new DataTransfer();
}
