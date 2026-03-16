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

    $('#w-exercises-listing').on('click', 'li.list-group-item', function(e) {
        // ignore the search input row
        if ($(this).find('#search-input').length) return;

        e.preventDefault();

        var id = $(this).data('id');
        var name = $(this).data('name') || '';
        if (!name) return;

        // ensure target list exists
        var $picked = $('#picked-exercises');
        if (!$picked.length) {
            $picked = $('<ul id="picked-exercises" class="list-group mt-3"></ul>').insertAfter('#exercises-listing');
        }

         // blink the clicked source item (add 'active' then remove after 1s)
        var $src = $(this);
        $src.addClass('active');
        setTimeout(function() { $src.removeClass('active'); }, 100);

        // create the new list item (with a remove button)
        var safeName = $('<div>').text(name).html();
        var $li = $(
        '<li class="list-group-item d-flex align-items-center" data-id="' + id + '">' +
            '<span class="picked-name flex-grow-1">' + safeName + '</span>' +
            '<input type="number" min="1" class="form-control form-control-sm picked-sets mx-2" placeholder="Sets" value="3" style="width:80px">' +
            '<input type="number" min="1" class="form-control form-control-sm picked-reps mx-2" placeholder="Reps" value="10" style="width:80px">' +
            '<button class="btn btn-sm btn-outline-danger remove-picked" type="button" aria-label="Remove ' + safeName + '">Remove</button>' +
        '</li>'
        );

        $picked.append($li);
        $li[0].scrollIntoView({ behavior: 'smooth', block: 'nearest' });

        
    });

    // remove picked item
    $('#picked-exercises').on('click', '.remove-picked', function(e){
        e.stopPropagation();           // don't trigger parent's click
        $(this).closest('li').remove();
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
        $.get('/fittrack/exercise_suggest/', { 'suggestion': query })
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

    $('#workout-search-input').on('keyup', function() {
        clearTimeout(typingTimer);
        var $this = $(this);
        typingTimer = setTimeout(function(){
        var query = $this.val();
        $.get('/fittrack/workout_suggest/', { 'suggestion': query })
            .done(function(data) {
            var $ul = $('#workouts-listing');
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
            var $ul = $('#w-exercises-listing');
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

    // jQuery AJAX that posts form + arrays of exercises to server
    (function($) {
    // read CSRF token from cookie (Django default)
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
            }
        }
        }
        return cookieValue;
    }

    $('#create-workout-btn').on('click', function () {
        var $btn = $(this);
        var $msg = $('#create-workout-msg').empty();
        var workoutName = $('#workout-name').val().trim();

        if (!workoutName) {
        $msg.text('Please enter a workout name.');
        return;
        }

        // gather picked exercises
        var $picked = $('#picked-exercises li[data-id]');
        if (!$picked.length) {
        $msg.text('Add at least one exercise to the picked list.');
        return;
        }

        var exercise_ids = [];
        var sets = [];
        var reps = [];
        var orders = [];

        $picked.each(function(index) {
        var $li = $(this);
        var exId = $li.data('id');
        var setVal = parseInt($li.find('.picked-sets').val(), 10) || 0;
        var repVal = parseInt($li.find('.picked-reps').val(), 10) || 0;
        // basic client validation
        if (!exId || setVal <= 0 || repVal <= 0) {
            // highlight problem row and stop
            $li.addClass('border border-danger');
            $msg.text('Each picked exercise must have valid sets and reps (> 0).');
            return false; // break out of each()
        }

        exercise_ids.push(exId);
        sets.push(setVal);
        reps.push(repVal);
        orders.push(index + 1);
        });

        if ($msg.text()) {
        // validation error found (message already set)
        return;
        }

        // disable UI while request runs
        var originalLabel = $btn.text();
        $btn.prop('disabled', true).text('Creating…');

        // Build data: workout name + arrays. jQuery will encode arrays like exercise_id[]=1&exercise_id[]=2
        var data = {
        name: workoutName
        };

        // append arrays using the bracket-syntax keys
        for (var i = 0; i < exercise_ids.length; i++) {
        data['exercise_id[]'] = data['exercise_id[]'] || [];
        data['exercise_id[]'].push(exercise_ids[i]);

        data['sets[]'] = data['sets[]'] || [];
        data['sets[]'].push(sets[i]);

        data['reps[]'] = data['reps[]'] || [];
        data['reps[]'].push(reps[i]);

        data['order[]'] = data['order[]'] || [];
        data['order[]'].push(orders[i]);
        }

        $.ajax({
        url: $('#create-workout-form').attr('action'),
        method: 'POST',
        data: data,
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        traditional: true, // ensure jQuery serializes arrays as exercise_id[]=1&exercise_id[]=2
        success: function(resp) {
            if (resp.success) {
            $msg.text('Workout created (id: ' + resp.workout_id + ').');
            window.location.reload();
            
            // clear UI or redirect
            $('#workout-name').val('');
            $('#picked-exercises').find('li[data-id]').remove();
            } else {
            $msg.text(resp.error || 'Failed to create workout.');
            }
        },
        error: function(xhr) {
            var text = 'Server error while creating workout.';
            try {
            var json = JSON.parse(xhr.responseText);
            text = json.error || text;
            } catch (e) {}
            $msg.text(text);
        },
        complete: function() {
            $btn.prop('disabled', false).text(originalLabel);
        }
        });

    });
    })(jQuery);

    

    // requires jQuery
    (function($){
    // reuse your getCookie helper for CSRF
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
            }
        }
        }
        return cookieValue;
    }

    // delegate handler for delete button inside workouts list
    $('#workouts-listing').on('click', '.delete-workout', function (e) {
        e.preventDefault();
        e.stopPropagation();

        var $btn = $(this);
        var workoutId = $btn.data('id');
        var workoutName = $btn.closest('li').data('name') || '';

        if (!workoutId) return;

        // confirm with the user — you can replace with a nicer modal if you have one
        if (!confirm('Delete workout "' + workoutName + '"? This will remove its exercises too.')) {
        return;
        }

        // optionally disable button while request runs
        $btn.prop('disabled', true).text('Deleting…');

        // POST to the same URL that WorkoutView handles (ensure your form/action is the view URL)
        var url = $('#create-workout-form').attr('action') || window.location.href;

        $.ajax({
        url: url,
        method: 'POST',
        data: {
            workout_id: workoutId,
            delete: '1'   // indicator for server to perform deletion
        },
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        success: function (resp) {
            if (resp.success) {
            // remove the list item with a fade
            var $li = $('#workouts-listing').find('li[data-id="' + resp.workout_id + '"]').first();
            if ($li.length) {
                $li.fadeOut(200, function(){ $(this).remove(); });

                // optional: if list is now empty, show "No workouts found." row
                if ($('#workouts-listing li[data-id]').length === 0) {
                $('#workouts-listing').append('<li class="list-group-item"><em>No workouts found.</em></li>');
                }
            } else {
                // fallback: reload if item not found
                // window.location.reload();
            }
            } else {
            alert(resp.error || 'Failed to delete workout.');
            $btn.prop('disabled', false).text('Delete');
            }
        },
        error: function (xhr) {
            var text = 'Server error while deleting workout.';
            try {
            var json = JSON.parse(xhr.responseText);
            text = json.error || text;
            } catch (e) {}
            alert(text);
            $btn.prop('disabled', false).text('Delete');
        }
        });
    });

    })(jQuery);

    

    
});