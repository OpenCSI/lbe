function showModalBox(url)
{
	$.ajax({
	   type: "GET",
	   url: url,
	   async:false,
	   success: function(data){
		    $('.addAttribute').html(data);
		    $('#MBAddAttribute').modal('show');
		}
	 });
}
