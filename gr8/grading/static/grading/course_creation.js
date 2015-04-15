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
});