$(document).ready(function() {
    // Auto-activate tabs
    if (location.hash !== '' && $('a[href="' + location.hash + '"]').length) $('a[href="' + location.hash + '"]').tab('show');
    $('a[data-toggle="tab"]').click(function() {
        location.hash = $(this).attr('href').substr(1);
    });
});
