function saveFormat()
{
	$.ajax({
	   type: "POST",
	   url: "/admin/format/modify/",
	   data: "formatID="+$('#formatID').val()+"&formatName=" +$('#formatName').val()+"&formatValue="+$('#formatValue').val(),
	   async:false,
	   success: function(data){
		    $('.message').html(data);
		    S = ($('.formatValue').is('disabled')==false?'*':'');
		    $('#sFormatName :checked').html($('#formatName').val() + ($('#formatName').val().charAt( $('#formatName').val().length-1 )!='*'?S:''));
		    $('#formatName').val($('#formatName').val() + ($('#formatName').val().charAt( $('#formatName').val().length-1 )!='*'?S:''));
		   }
	 });}

function deleteFormat(id)
{
	var res = confirm('Do you want to REMOVE the Format?');
	if (res)
		$.ajax({
		   type: "POST",
		   url: "/admin/format/modify/",
		   data: "deleteFID=" + id,
		   async:false,
		   success: function(data){
				$('.message').html(data);
			   }
	 });
}

function loadFormat(id)
{
	$.ajax({
	   type: "GET",
	   url: "/admin/format/modify/",
	   data: "format_id=" + id,
	   async:false,
	   success: function(data){
		    $('.modifyFormat').html(data);
		   }
	 });
}
