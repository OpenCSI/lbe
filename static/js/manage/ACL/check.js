/**
 * Function enables to check if the ACL's query is correct syntactically.
 **/
 function checkACL(query,id)
 {
	 $.ajax({
	   type: "GET",
	   url: "/admin/object/manage/",
	   data: "queryACL=" + query,
	   async:false,
	   success: function(data){
		    var pattern = /error/i;
		    if (data.match(pattern))
				$('#stateQueryACL'+id).attr('class','control-group error');
			else
				$('#stateQueryACL'+id).attr('class','control-group success');
		    $('#resultQueryACL'+id).html(data);
		   }
	 });
 }
 
 function showInfoACL()
 {
	 $.ajax({
	   type: "GET",
	   url: "/admin/object/manage/",
	   data: "showInfoACL",
	   async:false,
	   success: function(data){
		    $('.infoACL').html(data);
		    $('#showInfoACL').modal('show');
		   }
	 });
 }
