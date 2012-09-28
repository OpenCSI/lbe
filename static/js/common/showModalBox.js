function showModalBox(url,attribute)
{
	if (attribute)
		attr = 'attribute=' + attribute;
	else
		attr = '';
	$.ajax({
	   type: "GET",
	   url: url,
	   data: attr,
	   async:false,
	   success: function(data){
		    $('.addAttribute').html(data);
		    $('#MBAddAttribute').modal('show');
		}
	 });
}
