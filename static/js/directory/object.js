function showObject(id)
{
	$.ajax({
	   type: "GET",
	   url: "/directory/showObject",
	   data: "id=" + id,
	   async:false,
	   success: function(data){
		    $('#index').html(data);
		    $('#index').slideUp(0);
		    $('#index').slideDown("normal");
		   }
	 });
}

function showUserInformation(RDN,objectID)
{
	$.ajax({
	   type: "GET",
	   url: "/directory/showUser",
	   data: "id=" + RDN + '&objectID=' + objectID,
	   async:false,
	   success: function(data){
		    $('#index').html(data);
		    $('#index').slideUp(0);
		    $('#index').slideDown("normal");
		   }
	 });
}

function showUserAttribute(RDN,attribute,objectID)
{
	$.ajax({
	   type: "GET",
	   url: "/directory/modifyUser",
	   data: "id=" + RDN +'&attribute=' + attribute + '&objectID=' + objectID,
	   async:false,
	   success: function(data){
		    $('#showMBAttribute').html(data);
		    $('#showModifyAttribute').modal('show');
		   }
	 });
}

function addMultiValue()
{
	// Modify number value:
	$('#multivalue').attr('value',parseInt($('#multivalue').val())+1);
	// Add input type text:
	$('#multiValueInputADD').append('<tr><td>'+$('.attributeName').html()+'</td><td><input type="text" class="newValue" name="newValue" value=""/></td></tr>');
}

function saveModificationUser()
{
	attrLDAP = $('#attributeLDAP').val();
	if ($('#multivalue').val() == 0)
	{
		newValue = $('.newValue').val(); 
		oldValue = $('.oldValue').val(); 
	}
	else
	{
		newValue = '';
		$('.newValue').each(function(){
			newValue += $(this).val() + ',';
		});
		newValue = newValue.slice(0,newValue.length-1);
		oldValue = '';
		$('.oldValue').each(function(){
			oldValue += $(this).val() + ',';
		});
		oldValue = oldValue.slice(0,oldValue.length-1);
	}
	$.ajax({
	   type: "POST",
	   url: "/directory/modifyUser",
	   data: "RDN=" + $('#RDN').val() +'&attributeLDAP=' + $('#attributeLDAP').val() + '&objectID=' + $('#objectID').val() +'&newValue='+ newValue + '&oldValue=' + oldValue + '&multivalue=' + $('#multivalue').val(),
	   async:false,
	   success: function(data){
		    $('#showModifyAttribute').modal('hide');
		    $('#showMBAttribute').html(data);
		   }
	 });
}

function deleteValue(RDN,objectID,LDAP)
{
	$.ajax({
	   type: "POST",
	   url: "/directory/modifyUser",
	   data: "type=delete&RDN=" + RDN + '&objectID=' + objectID + '&attributeLDAP=' + LDAP,
	   async:false,
	   success: function(data){
		    $('#showMBAttribute').html(data);
		   }
	 });
}
