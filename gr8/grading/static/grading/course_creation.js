var pending_lookup;
var form_submitting = false;

function get_form_data() {
    data = {}
    $("#course-form *").filter(":input").each(function() {
        data[this.name] = $(this).val();
    });
    return data;
}

function clear_form() {
    // TODO implement
    $("#course-form *").filter(":input[type!='hidden']").each(function() {
        $(this).val(null);
    });
    // also reset the 'found course' text
    $("#found-course-name").html("");
}

// Sets the status <h2> on the page and sets it to text-danger
// param message not required, defaults to a generic error
function set_error(message) {
    $("#status").hide();
    if (message) {
        $("#status").html(message);
    } else {
        $("#status").html("Course was not created due to an error");
    }
    $("#status").addClass("text-danger");
    $("#status").show();
    console.log(message);
}

// Sets the status <h2> on the page and makes it not text-danger
// param message required.
function set_status(message) {
    $("#status").hide().html(message).removeClass("text-danger").show();
}


function validate_course_form(callback) {
    // build up the data object
    data = get_form_data();
    // send it off to the ajaxes
    $.ajax({
        url: '/ajax/validate_course',
        method: 'GET',
        data: data,
        success: function(response) {
            if (response.success) {
                callback(response);
            } else {
                console.log(response.errors);
                form_submitting = false;
            }
            $("#course-form *").filter(":input").each(function() {
                var name = this.name;
                // if an error was reported with this element
                if (response.errors[name]) {
                    // set the error class and message
                    $(this).parent().addClass("entry-error");
                    $("#" + name + "-errors").html(response.errors[name]);
                } else {
                    // need to ` out the errors
                    $(this).parent().removeClass("entry-error");
                    $("#" + name + "-errors").html("");
                }
            })
        },
        error: function(response) {
            set_error("An error occured while validating form");
            form_submitting = false; // Stuff won't continue to the next part.
        }
    })
}

function submit_course_form(callback) {
    // WARNING: HACKERS PLEASE DO NOT CALL THIS METHOD AS IT WILL BREAK OUR SYSTEM
    // Thanks
    // We trust you.
    $.ajax({
        url: '/ajax/submit_course',
        method: "POST",
        data: get_form_data(),
        success: function(response) {
            if (response.success) {
                set_status("Course '" + response.course_name + "' added.");
                clear_form();
                // TODO set success thingy
            } else {
                set_error("Form contains errors. Please fix the highlighted fields.");
                // Oh well :(
            }
        },
        error: function() {
            set_error("An error occurred while submitting form");

        },
        complete: function() {
            form_submitting = false;
        }
    })
}

function click_button() {
    if (!form_submitting) { // prevents a user from submitting the same form twice by double-clicking or pressing enter.
        validate_course_form(submit_course_form)
        form_submitting = true;
    }
}

//////////////////////////////////////
// course session adding functionality

function make_checkbox_cell(name) {
    var cell = document.createElement("TD");
    cell.className = "form-group";
    var div = document.createElement("DIV");
    div.className = "entry";
    cell.style = "text-align: center;";
    var checkbox = document.createElement("INPUT");
    checkbox.type = "checkbox";
    checkbox.name = name;
    checkbox.value = false;
    div.appendChild(checkbox);
    cell.appendChild(div);
    return cell;
}

function make_text_cell(name, placeholder) {
    var cell = document.createElement("TD");
    cell.className = "form-group";
    var div = document.createElement("DIV");
    div.className = "entry";
    var textbox = document.createElement("INPUT");
    textbox.type = "text";
    textbox.name = name;
    textbox.value = null;
    if (placeholder) {
        textbox.placeholder = placeholder;
    }
    div.appendChild(textbox);
    cell.appendChild(div);
    return cell;
}

function make_minus_cell() {
    var cell = document.createElement("TD");
    cell.className = "sign";
    var a = document.createElement("A");
    a.href="javascript:;";
    a.appendChild(create_glyphicon("glyphicon-minus-sign", "red", 20));
    cell.appendChild(a);
    $(a).click(function() {
        var row = this.parentNode.parentNode;
        document.getElementById('session-table').removeChild(row);
    });
    return cell;
}

function make_session_row(minus) {
    // construct the row
    var row = document.createElement("TR");
    var cell;

    // do some cells
    row.appendChild(make_checkbox_cell("monday"));
    row.appendChild(make_checkbox_cell("tuesday"));
    row.appendChild(make_checkbox_cell("wednesday"));
    row.appendChild(make_checkbox_cell("thursday"));
    row.appendChild(make_checkbox_cell("friday"));
    row.appendChild(make_checkbox_cell("saturday"));
    row.appendChild(make_checkbox_cell("sunday"));
    // do the cells with times
    row.appendChild(make_text_cell("start-time", 'HH:MM'));
    row.appendChild(make_text_cell("end-time", 'HH:MM'));
    row.appendChild(make_text_cell("room", "Room"));
    if (minus) {
        row.appendChild(make_minus_cell());
    }
    return row;
}


// on load
$(document).ready(function() {
    document.getElementById('id_code').addEventListener("keyup", function() {
        clearTimeout(pending_lookup); // wait until the user is finished typing.
        pending_lookup = setTimeout(function() {update_course_name($("#id_code").val(), 'found-course-name');}, 1000);
    });
    $("#course-form :input").on("keyup", function(e) {
        if (e.keyCode === 13) {
            click_button();
        }
    });

    document.getElementById('session-table').appendChild(make_session_row());
    $("#session-add-button").click(function() {
        document.getElementById('session-table').appendChild(make_session_row(true));
    });
});