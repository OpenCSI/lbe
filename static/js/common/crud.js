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
				$('.'+attribute).html(data);
				//$('#'+attribute).focus();
			}
		 });
}

/*function toText(attribute,value)
{
	$('.'+attribute).html(value);
}*/
