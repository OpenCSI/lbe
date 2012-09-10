function showMBAddAttribute(id)
{
	$.ajax({
	   type: "GET",
	   url: "/ajax/config/object/modify/" + id,
	   async:false,
	   success: function(data){
		    $('.addAttribute').html(data);
		    $('#MBAddAttribute').modal('show');
		}
	 });
}
