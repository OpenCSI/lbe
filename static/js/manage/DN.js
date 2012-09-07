function showDN()
{
	$.ajax({
	   type: "GET",
	   url: "/admin/object/DN/",
	   data: "type=showDN",
	   async:false,
	   success: function(data){
		    $('#showDN').html(data);
		    $('#showTreeDN').modal('show');
		   }
	 });
}
