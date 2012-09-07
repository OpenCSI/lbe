function loadReference(id)
{
	$.ajax({
	   type: "GET",
	   url: "/admin/reference/manage/",
	   data: "reference_id=" + id,
	   async:false,
	   success: function(data){
		    $('.modifyReference').html(data);
		   }
	 });
}

function deleteReference(id)
{
	if (confirm('Do you want to DELETE the Reference?'))
		$.ajax({
		   type: "POST",
		   url: "/admin/reference/delete/",
		   data: "reference_id=" + id,
		   async:false,
		   success: function(data){
				$('.modifyReference').html(data);
			   }
		 });
}

function loadAttribute()
{
	$.ajax({
	   type: "GET",
	   url: "/admin/reference/manage/",
	   data: "objectID=" + $('.objectID').val(),
	   async:false,
	   success: function(data){
		    $('.referValue').html(data);
		   }
	 });
}
