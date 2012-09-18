function addField(attribute)
{
	$('.'+attribute).append("<input type='text' name='"+attribute+"' id='id_"+attribute+"' value=''/><br>");
}
