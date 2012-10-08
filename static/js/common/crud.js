function selectFrom(url,attribute)
{
	$.ajax({
	   type: "GET",
	   url: url + attribute + '/' + $('#id_'+attribute).val(),
	   async:false,
	   success: function(data){
		    $('.show').html(data);
		}
	 });
}

function update(url,attribute,value,num)
{
	if (num)
		id = '_' + num.split(';')[1];
	else
		id = '';
	attr = attribute + id; 
	if ($('#id_'+attribute).val() == null)
		$.ajax({
		   type: "GET",
		   url: url + '/modify/',
		   data: attr +'=' + value,
		   async:false,
		   success: function(data){
				$('.'+attr).html(data);
				$('#id_'+attribute).focus();
			}
		 });
}

function save(url,attribute,value,num)
{
	if (num)
		id = '_' + num;
	else
		id = '';
	attr = attribute + id;
	if ($('#id_'+attribute).val() != null)
		$.ajax({
		   type: "GET",
		   url: url + '/save/',
		   data: attr + '=' + value,
		   async:false,
		   success: function(data){
				toText(attribute,data,num);
			}
		 });
}

function toText(attribute,value,num)
{
	if (num)
		id = '_' + num;
	else
		id = '';
	if (value == '')
		val = '<i>No Value</i>'
	else
		val = value
		$('.'+attribute+id).html(val);
	// Replace value into function from onClick event:
	var tab = $('.'+attribute+id).attr("onClick").split(',');
	tab[2] = "'"+ value + "');";
	$('.'+attribute+id).attr("onClick",tab[0]+','+tab[1]+','+tab[2])
}

function add(url,attribute,value)
{
	$.ajax({
	   type: "GET",
	   url: url + '/add/',
	   data: attribute + '_-1=' + value,
	   async:false,
	   success: function(data){
			$('.message').html(data);
			$('#MBAddAttribute').modal('hide');
		}
	 });
}

function check(url,attribute,value)
{
	$.ajax({
	   type: "GET",
	   url: url,
	   data: attribute + '=' + value,
	   async:false,
	   success: function(data){
			if (data == 0)
			{
				$('#create').removeAttr('disabled');
				$('.state').html('Value is correct.');
				$('.state').css('color','green');
			}
			else if (data == -1)
			{
				$('#create').attr('disabled','disabled');
				$('.state').html('Cannot create empty value.');
				$('.state').css('color','red');
			}
			else if (data == -2)
			{
				$('#create').attr('disabled','disabled');
				$('.state').html('The value syntax is incorrect.');
				$('.state').css('color','red');
			}
		}
	 });
}
