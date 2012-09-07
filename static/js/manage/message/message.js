function showMessages(type)
{
	$.ajax({
	   type: "GET",
	   url: "/admin/message/ajax/",
	   data: "tab=" + type,
	   async:false,
	   success: function(data){
		    $('.content').html(data);
		   }
	 });
}

function checkAll(field)
{
	for (i = 0; i < field.length; i++)
		field[i].checked = true ;
}
