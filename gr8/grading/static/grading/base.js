var pending_lookup;
$(".course-row").click(function() {
    window.location = "/course/" + this.id;
});

function update_course_name(code, id) {
	$.ajax({
		url: '/ajax/lookup_code',
		dataType: 'json',
		data: {
			code: code
		},
		success: function(response) {
			$("#" + id).html(response.name);
		}
	});
}

// A simple function to determine if a course-row contains a given string.
// TODO Make this ignore html tags because that's probably a good idea.
function row_contains_str(row, string) {
	return $(row).html().toUpperCase().indexOf(string.toUpperCase()) !== -1;
}

function filter_courses(str) {
	$(".course-row").each(function() {
		if (row_contains_str(this, str)) {
			$(this).show();
		} else {
			$(this).hide();
		}
	});
}


document.getElementById('searchbox').addEventListener("keyup", function() {
	filter_courses($('#searchbox').val());
});

document.getElementById('id_code').addEventListener("keyup", function() {
	clearTimeout(pending_lookup); // wait until the user is finished typing.
	pending_lookup = setTimeout(function() {update_course_name($("#id_code").val(), 'found-course-name');}, 1000);
});