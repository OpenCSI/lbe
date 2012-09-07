function showMBCreate()
{
	$.ajax({
	   type: "GET",
	   url: "/admin/object/modify/",
	   data: "createAttribute=true",
	   async:false,
	   success: function(data){
		    $('.MBAttribute').html(data);
		    $('#showCreateAttribute').modal('show');
		   }
	 });
}

function createAttr()
{
	$.ajax({
	   type: "POST",
	   url: "/admin/object/modify/",
	   data: "attribute_create=true&attribute_name=" + $('#attribute_name').val()+ "&attribute_Dname=" + $('#attribute_Dname').val() + "&mandatory=" + $('#mandatory').attr('checked') +
	   "&multivalue=" + $('#multivalue').attr('checked') + "&isvirtual=" + $('#isVirtual').attr('checked') + '&virtual=' + $('#listVirtual :checked').val() +
	   "&defaultvalue=" + $('#defaultvalue').val() + "&object=" + $('#objectName :checked').val()+"&attribute_format=" + $('#listFormat :checked').val()+ '&isreference=' + $('#isReference').attr('checked') +
	   '&reference=' + $('#listReference :checked').val() + "&encrypt=" + $('#encrypt :checked').val(),
	   async:false,
	   success: function(data){
		    var patt = /alert-success/i;
		    if (data.match(patt))
		    {
				$('.message').html(data);
			    $('#showCreateAttribute').modal('hide');
				loadObjectAttribute($('#objectName :checked').val());
			}
			else
			{   
				$('.res').html(data);
				$('.message').html('');
			}
		   }
	 });
}
