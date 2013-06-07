function showRootDirectory()
{
	$.ajax({
	   type: "GET",
	   url: "/directory/show",
	   data: "showDirectory=true",
	   async:false,
	   success: function(data){
		    $('#index').html(data);
		    $('#index').slideUp(0);
		    $('#index').slideDown("normal");
		   }
	 });
}

function changeLoadME(value,id,me)
{
	if ($('#'+me).hasClass('icon-chevron-right'))
	{
		$('#'+me).attr('class','icon-chevron-down');
		$('#value'+me).wrapInner(document.createElement("b"));
		// Load list & values:
		loadDirectoryfrom(value,id,'lvl' + id*10)
	}
	else
	{
		$('#'+me).attr('class','icon-chevron-right');
		value = $('#value'+me).find("b").html();
		$('#value'+me).html(value);
		$('#lvl'+(id==0?id:id*10)).slideUp("normal");
	}
}

function loadDirectoryfrom(value,id,to)
{
	$.ajax({
	   type: "GET",
	   url: "/directory/list",
	   data: "getDirectory=" + value + "&id=" + (id*10),
	   async:false,
	   success: function(data){
		    $('#'+to).html(data);
		    $('#'+to).slideUp(0);
		    $('#'+to).slideDown("normal");
		   }
	 });
}

function search(e,object,pattern)
{
	if (e.which == 13)
		$.ajax({
		   type: "GET",
		   url: "/ajax/directory/search/" + object + "/" + pattern,
		   async:false,
		   success: function(data){
			    if (data == "/")
				   window.location.href=data;
			    else
			    {
					$('.Tdata').text('');
					$('.Tdata').html(data);
				}
			   }
		 });
}

