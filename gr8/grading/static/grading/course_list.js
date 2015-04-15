$(document).ready(function() {
    document.getElementById('searchbox').addEventListener("keyup", function() {
        filter_courses($('#searchbox').val());
    });
});