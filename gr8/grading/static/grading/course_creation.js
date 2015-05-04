var pending_lookup;
var form_submitting = false;
var validation_failed = false;
var course_id = null;

function get_form_data() {
    data = {}
    $("#course-form *").filter(":input").each(function() {
        data[this.name] = $(this).val();
    });
    return data;
}

function clear_form() {
    $("#course-form *").filter(":input[type!='hidden']").each(function() {
        $(this).val(null);
    });
    // also reset the 'found course' text
    $("#found-course-name").html("");
    // also clear all the course things
    $(".session-row :input").each(function() {
        $(this).val(null);
        // for checkboxes
        $(this).attr("checked", null);
    });
}

function reset_errors() {
    $(".session-row .entry-error").removeClass("entry-error");
}

// Sets the status <h2> on the page and sets it to text-danger
// param message not required, defaults to a generic error
function set_error(message) {
    $("#status-flash").hide();
    if (message) {
        $("#status-flash").html(message);
    } else {
        $("#status-flash").html("Course was not created due to an error");
    }
    $("#status-flash").addClass("alert-danger");
    $("#status-flash").show();
    console.log(message);
}

// Sets the status <h2> on the page and makes it not text-danger
// param message required.
function set_status(message) {
    $("#status-flash").hide();
    if (message) {
        $("#status-flash").html(message);
        $("#status-flash").removeClass("alert-danger");
        $("#status-flash").addClass("alert-success");
        $("#status-flash").show();
    }
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
            if (!response.success) {
                validation_failed = true;
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
        },
        complete: function(response) {
            callback(response)
        }
    })
}

function submit_course_form(callback) {
    // WARNING: HACKERS PLEASE DO NOT CALL THIS METHOD AS IT WILL BREAK OUR SYSTEM
    // Thanks
    // We trust you.
    if (validation_failed) {
        // reset validation flag, return.
        validation_failed = false;
        // u dun gooft
        set_error("There were errors in the form. Please fix the highlighted fields and submit again");
        return;
    }
    $.ajax({
        url: '/ajax/submit_course',
        method: "POST",
        data: get_form_data(),
        success: function(response) {
            if (response.success) {
                set_status("Course '" + response.course_name + "' added.");
                course_id = response.course_id;
                callback();
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
        validate_course_form(function() {
            validate_session(document.getElementsByClassName('session-row')[0], function() {
                submit_course_form(function() {
                    submit_session($(".session-row")[0], function() {
                        clear_form();
                    });
                });
            });
        });
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
    row.className = "session-row";
    var cell;

    // do some cells
    row.appendChild(make_checkbox_cell("Monday"));
    row.appendChild(make_checkbox_cell("Tuesday"));
    row.appendChild(make_checkbox_cell("Wednesday"));
    row.appendChild(make_checkbox_cell("Thursday"));
    row.appendChild(make_checkbox_cell("Friday"));
    row.appendChild(make_checkbox_cell("Saturday"));
    row.appendChild(make_checkbox_cell("Sunday"));
    // do the cells with times
    row.appendChild(make_text_cell("start-time", 'HH:MM'));
    row.appendChild(make_text_cell("end-time", 'HH:MM'));
    row.appendChild(make_text_cell("room", "Room"));
    if (minus) {
        row.appendChild(make_minus_cell());
    }
    return row;
}

////////////////////////////////
// How to ajax the sessions

function get_session_data(row) {
    var sess = {};
    $('input', $(row)).each(function() {
        if (this.type === "checkbox") {
            sess[this.name] = $(this).is(":checked");
        } else {
            sess[this.name] = $(this).val();
        }
    });
    sess.csrfmiddlewaretoken = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    sess["course-id"] = course_id;

    return sess;
}


// validate a session row.
function validate_session(row, finished) {
    if (!row) {
        // done looping, do callback
        finished();
        return; 
    }
    var session = get_session_data(row);
    $.ajax({
        url: '/ajax/validate_session',
        method: "GET",
        data: session,
        success: function(response) {
            console.log(response);
            if (!response.success) {
                form_submitting = false;
                validation_failed = true; // mark as failed
                reset_errors();
                for (key in response.errors) {
                    $(row).find("[name="+key+"]").parent().addClass("entry-error")
                }
            }
        },
        complete: function(response) {
            validate_session(row.nextSibling, finished)
        }
    });
}

function submit_session(row, finished) {
    if (row == null) {
        // no more rows, clear the form
        if (finished) {
            finished()
        }
        return
    }
    var session = get_session_data(row);
    $.ajax({
        url: '/ajax/submit_session',
        method: "POST",
        data: session,
        success: function(response) {
            if (response.success) {
                submit_session(row.nextSibling, finished);
            } else {
                set_error("An error occurred while submitting the course sessions");
            }
        },
        error: function(response) {
            set_error("An error occurred while submitting the course sessions");
            form_submitting = false;
            //TODO STUFF
        }
    })
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

    document.getElementById('session-table').appendChild(make_session_row(true));
    $("#session-add-button").click(function() {
        document.getElementById('session-table').appendChild(make_session_row(true));
    });
});