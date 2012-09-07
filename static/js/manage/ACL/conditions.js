/**
 * functions enable admin to proceed modify/delete ACL.
 **/

// attr : for special ACL attribute
function loadConditions(typeACL,objectName,attr)
{
	$.ajax({
	   type: "GET",
	   url: "/admin/object/manage/",
	   data: "typeACL=" + typeACL + "&object=" + objectName + (attr!='' ?"&specialAttribute=" + attr : ''),
	   async:false,
	   success: function(data){
		    if (attr == '')
				$('.conditions').html(data);
			else
				$('#specialConditions').html(data);
		   }
	 });
}

function modifyACL(id,attr)
{
	$.ajax({
	   type: "GET",
	   url: "/admin/object/manage/",
	   data: "edit_id=" + id + (attr!='' ?"&specialAttribute=" + attr : ''),
	   async:false,
	   success: function(data){
		    if (attr == '')
		    {
				$('.'+id).html(data);
				$('.'+id).fadeIn(0);
			}
			else
			{
				$('.Special'+id).html(data);
				$('.Special'+id).fadeIn(0);
			}
		   }
	 });
}

function askForDeleteACL(id,attr)
{
	// messagebox Warning:
	var res = confirm('Voulez-vous vraiment supprimer l\'acl?');
	// OK -> Ajax:
	if (res)
		deletedACL(id,attr);
}
