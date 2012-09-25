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

function update(url,attribute,value)
{
	if ($('#'+attribute).val() == null)
		$.ajax({
		   type: "GET",
		   url: url + '/modify/',
		   data: attribute + '=' + value,
		   async:false,
		   success: function(data){
				$('.'+attribute).html(data);
				$('#'+attribute).focus();
			}
		 });
}

function save(url,attribute,value)
{
	if ($('#'+attribute).val() != null)
		$.ajax({
		   type: "GET",
		   url: url + '/save/',
		   data: attribute + '=' + value,
		   async:false,
		   success: function(data){
				toText(attribute,data);
			}
		 });
}

function toText(attribute,value)
{
	$('.'+attribute).html(value);
	// Replace value into function from onClick event:
	var tab = $('.'+attribute).attr("onClick").split(',');
	tab[2] = "'"+ value + "');";
	$('.'+attribute).attr("onClick",tab[0]+','+tab[1]+','+tab[2])

}
