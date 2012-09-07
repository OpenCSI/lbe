function modifyAttribute(id)
{
	$.ajax({
	   type: "GET",
	   url: "/admin/object/modify/",
	   data: "attribute_id=" + id+ "&object=" + $('#objectName :checked').val(),
	   async:false,
	   success: function(data){
		    $('.MBAttribute').html(data);
		    $('#showModify').modal('show');
		   }
	 });
}

function loadObjectAttribute(objectName)
{
	$.ajax({
	   type: "GET",
	   url: "/admin/object/modify/",
	   data: "loadObject=" + objectName,
	   async:false,
	   success: function(data){
		    $('.object').html(data);
		   }
	 });
}

function saveAttributes(id)
{
	$.ajax({
	   type: "POST",
	   url: "/admin/object/modify/",
	   data: "attribute_id=" + id + "&attribute_name=" + $('#attribute_name').val()+ "&mandatory=" + $('#mandatory').attr('checked') +
	   "&multivalue=" + $('#multivalue').attr('checked') + "&isvirtual=" + $('#isVirtual').attr('checked') + '&virtual=' + $('#listVirtual :checked').val() +
	   "&defaultvalue=" + $('#defaultvalue').val() + "&attribute_format=" + $('#listFormat :checked').val() + '&isreference=' + $('#isReference').attr('checked') +
	   '&reference=' + $('#listReference :checked').val() + "&object=" + $('#objectName :checked').val() + "&encrypt=" + $('#encrypt :checked').val(),
	   async:false,
	   success: function(data){
		    $('.message').html(data);
		    $('#showModify').modal('hide');
		    loadObjectAttribute($('#objectName :checked').val());
		   }
	 });
}

function deleteAttribute(id)
{
	// messagebox Warning:
	var res = confirm('Do you want to REMOVE the attribute?');
	if (res)
		$.ajax({
		   type: "POST",
		   url: "/admin/object/modify/",
		   data: "IDAttributeToRemove=" + id+'&object=' + $('#objectName :checked').val(),
		   async:false,
		   success: function(data){
			    loadObjectAttribute($('#objectName :checked').val());
				$('.message').html(data);
			   }
	 });
}

function locked(type)
{
	if (type == "V")
	{
		if ($('#isVirtual').attr('checked') == 'checked')
		{
			$('#defaultvalue').attr("disabled", true);
			$('#listReference').attr("disabled", true);
			$('#listVirtual').removeAttr("disabled"); 
			$('#isReference').removeAttr("checked"); 
		}
		else
		{
			$('#defaultvalue').removeAttr("disabled"); 
			$('#listVirtual').attr("disabled", true);	
		}
	}
	else if (type == "R")
	{
		if ($('#isReference').attr('checked') == 'checked')
		{
			$('#defaultvalue').attr("disabled", true);
			$('#listVirtual').attr("disabled", true);
			$('#listReference').removeAttr("disabled"); 
			$('#isVirtual').removeAttr("checked"); 
		}
		else
		{
			$('#defaultvalue').removeAttr("disabled"); 
			$('#listReference').attr("disabled", true);
		}
	}
}
