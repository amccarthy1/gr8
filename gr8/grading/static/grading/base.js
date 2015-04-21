$(".course-row").click(function() {
    window.location = "/course/" + this.id;
});

$(function() {
    $('.tooltip-wrapper').tooltip({position: "left"});
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

// returns an HTML dom object representing the chosen glyphicon
function create_glyphicon(name, color) {
	var span = document.createElement("SPAN");
	span.className = "glyphicon " + name;
	if (color) {
		span.style="color:" + color + ";";
	}
	return span;
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