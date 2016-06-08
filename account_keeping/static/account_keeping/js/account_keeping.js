$(document).ready(function() {
    // Auto-activate tabs
    if (location.hash !== '' && $('a[href="' + location.hash + '"]').length) $('a[href="' + location.hash + '"]').tab('show');
    $('a[data-toggle="tab"]').click(function() {
        location.hash = $(this).attr('href').substr(1);
    });

    // Show/hide 'mark invoice' field
    $('[data-id="invoice-field"]').change(function() {
        if ($(this).val()) {
            $('[data-id="mark-invoice-field"]').parents('label').show();
        } else {
            $('[data-id="mark-invoice-field"]').parents('label').hide();
        }
    }).change();
});
