/**
 * functions make actions on ACL [delete/create/update].
 **/
 
function createACL()
{
	$.ajax({
	   type: "POST",
	   url: "/admin/object/manage/",
	   data: "create_type=" + $('#typeACL :selected').val() + "&create_language=" + $('.lang:checked').val()  + "&create_object=" + $('#objectName :selected').val() + "&create_condition="+ $('#textCreate').val(),
	   async:false,
	   success: function(data){
			// sucessfull
			$('.conditions').html(data);
		   }
	 });
}

function createSpecialACL()
{
	$.ajax({
	   type: "POST",
	   url: "/admin/object/manage/",
	   data: "create_type=" + $('#listSpecialACL :checked').val() + "&create_language=" + $('#selectSpecialLang :checked').val() + "&create_object=" + $('#objectName :selected').val() + "&create_condition="+ $('#textSpecialCreateACL').val()+"&specialAttribute=" + $('#AttrTitle').html(),
	   async:false,
	   success: function(data){
			$('#specialConditions').html(data);
		   }
	 });
}

function modifiedACL(id,attr)
{
	$.ajax({
	   type: "POST",
	   url: "/admin/object/manage/",
	   data: "edit_id=" + id + "&edit_condition=" + (attr!='' ?$('#textModifySpecial').val():$('#textModify').val()) + "&edit_lang=" + (attr!=''?$('#selectSpecialLang :checked').val():$('#editLang :selected').val()) + (attr!='' ?"&specialAttribute=" + attr : ''),
	   async:false,
	   success: function(data){
			if (attr == '')
				$('.conditions').html(data);
			else
				$('#specialConditions').html(data);
		   }
	 });
}

function deletedACL(id,attr)
{
	$.ajax({
	   type: "POST",
	   url: "/admin/object/manage/",
	   data: "delete_id=" + id + (attr!='' ?"&specialAttribute=" + attr : ''),
	   async:false,
	   success: function(data){
		    if (attr == '')
				$('.conditions').html(data);
			else
				$('#specialConditions').html(data);
		   }
	 });
}

function showFormat(id)
{
	$.ajax({
	   type: "POST",
	   url: "/admin/object/manage/",
	   data: "format_id=" + id,
	   async:false,
	   success: function(data){
		    //$('.conditions').html(data);
		   }
	 });
}
