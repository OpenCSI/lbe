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

function showModalBox1V(url,val)
{
	$.ajax({
	   type: "GET",
	   url: url + val,
	   async:false,
	   success: function(data){
		    $('.show').html(data);
		    $('#MBAddAttribute').modal('show');
		}
	 });
}
