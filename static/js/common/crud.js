function selectFrom(url,attribute)
{
	$.ajax({
	   type: "GET",
	   url: url + attribute + '/' + $('#id_'+attribute).val(),
	   async:false,
	   success: function(data){
		    $('.show').html(data);
		}
	 });
}

function update(url,attribute,value,num)
{
	if (num)
		id = '_' + num.split(';')[1];
	else
		id = '';
	attr = attribute + id; 
	if ($('#id_'+attribute).val() == null)
		$.ajax({
		   type: "GET",
		   url: url + '/modify/',
		   data: attr +'=' + value,
		   async:false,
		   success: function(data){
				$('.'+attr).html(data);
				$('#id_'+attribute).focus();
			}
		 });
}

function save(url,attribute,value,num)
{
	if (num)
		id = '_' + num;
	else
		id = '';
	attr = attribute + id;
	if ($('#id_'+attribute).val() != null)
		$.ajax({
		   type: "GET",
		   url: url + '/save/',
		   data: attr + '=' + value,
		   async:false,
		   success: function(data){
				toText(attribute,data,num);
			}
		 });
}

function toText(attribute,value,num)
{
	if (num)
		id = '_' + num;
	else
		id = '';
	$('.'+attribute+id).html(value);
	// Replace value into function from onClick event:
	var tab = $('.'+attribute+id).attr("onClick").split(',');
	tab[2] = "'"+ value + "');";
	$('.'+attribute+id).attr("onClick",tab[0]+','+tab[1]+','+tab[2])

}
