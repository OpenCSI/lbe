function approve(objectID,id)
{
	$.ajax({
	   type: "GET",
	   url: "/directory/approvale/" + objectID,
	   data: "id=" + id + '&approve',
	   async:false,
	   success: function(data){
		    $('body').html(data);
		   }
	 });
}

function refuse(objectID,id)
{
	$.ajax({
	   type: "GET",
	   url: "/directory/approvale/" + objectID,
	   data: "id=" + id + '&refuse',
	   async:false,
	   success: function(data){
		    $('body').html(data);
		   }
	 });
}
