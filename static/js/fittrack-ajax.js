console.log("JS loaded");
$(document).ready(function() {

    $('#exercises-listing').on('click', 'li.list-group-item', function(e) {
        // ignore the search input row (if you left it inside the ul)
        if ($(this).find('#search-input').length) {
            return;
        }

        e.preventDefault();

        var id = $(this).data('id');
        var name = $(this).data('name') || '';
        var bodypart = $(this).data('bodypart') || '';

        // populate hidden id and form fields
        $('#edit-id').val(id);
        $('#edit-name').val(name);
        $('#edit-body-part').val(bodypart);

        // visual cue for selected item
        $('#exercises-listing .list-group-item').removeClass('active');
        $(this).addClass('active');

        // focus name field for quick editing
        $('#edit-name').focus();
    });

    $('#delete-exercise-btn').on('click', function(e) {
        var ok = confirm('Are you sure you want to delete this exercise? This cannot be undone.');
        if (!ok) {
        // stop the submit
        e.preventDefault();
        return false;
        }
        // otherwise allow submit to go through
    });

    // clear button to reset the form
    $('#clear-edit-btn').on('click', function() {
        $('#edit-id').val('');
        $('#edit-name').val('');
        $('#edit-body-part').val('');
        $('.list-group-item').removeClass('active');
    });


    $('#like-btn').click(function() {
        var categoryIdVar;
        categoryIdVar = $(this).attr('data-categoryid');

        $.get('/rango/like_category/',
            {'category_id': categoryIdVar},
            function(data) {
                $('#like-count').html(data);
                $('#like-btn').hide();
            })
    });

    (function($){
    var typingTimer;
    var doneTypingInterval = 200;

    $('#exercise-search-input').on('keyup', function() {
        clearTimeout(typingTimer);
        var $this = $(this);
        typingTimer = setTimeout(function(){
        var query = $this.val();
        $.get('/fittrack/suggest/', { 'suggestion': query })
            .done(function(data) {
            var $ul = $('#exercises-listing');
            $ul.empty();
            $ul.append(data);
            })
            .fail(function() {
            console.error('Suggest request failed');
            });
        }, doneTypingInterval);
    });

  // If user pauses typing -> trigger immediately; if they keep typing, waits.
})(jQuery);

    
});