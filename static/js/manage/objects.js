/**
 * functions enable to load/manage Objects [attributes]
 **/

function loadObject(objectName)
{
	$.ajax({
	   type: "GET",
	   url: "/admin/object/manage/",
	   data: "loadObject=" + objectName,
	   async:false,
	   success: function(data){
		    $('.object').html(data);
		   }
	 });
}

function saveApprove(value)
{
	$.ajax({
	   type: "POST",
	   url: "/admin/object/modify/",
	   data: 'object=' + $('#objectName :checked').val() + '&approval=' + value,
	   async:false,
	   success: function(data){
		    $('.message').html(data);
		   }
	 });
}

function showModifyAttrACL(id)
{
	$.ajax({
	   type: "GET",
	   url: "/admin/object/manage/",
	   data: "attribute_id=" + id + '&object=' + $('#objectName :checked').val(),
	   async:false,
	   success: function(data){
		    $('.showModifyBox').html(data);
		    $('#showModify').modal('show');
		   }
	 });
}
