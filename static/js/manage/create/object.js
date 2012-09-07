function addObjectClass()
{
	val = $('#objectClass').val();
	if (val != '')
	{
		html = $('#class').html();
		html += '<span id=' + val + '><input type="hidden" name="HobjectClass" value="'+ val +'" />' + val + '<a href="#" class="icon-trash" onClick="del(\''+val+'\');"></a><br></span>';
		$('#class').html(html);
		$('#objectClass').val('');
	}
}

function addObjectAttribute()
{
	val = $('#objectAttribute').val();
	if (val != '')
	{
		html = $('#attributes').html();
		html += '<span id=' + val + '><input type="hidden" name="HobjectAttribute" value="'+ val +'"/>' + val + '<a href="#" class="icon-trash" onClick="del(\''+val+'\');"></a><br></span>';
		$('#attributes').html(html);
		$('#objectAttribute').val('');
	}
}

function del(val)
{
	var d = document.getElementById(val);
	d.parentNode.removeChild(d); 
}
