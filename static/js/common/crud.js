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
