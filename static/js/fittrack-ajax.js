
$(document).ready(function ($) {
  'use strict';

  // ---- Helpers ------------------------------------------------------------
  const $doc = $(document);

  // Read cookie
  const getCookie = (name) => {
    const cookies = document.cookie ? document.cookie.split(';') : [];
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        return decodeURIComponent(cookie.substring(name.length + 1));
      }
    }
    return null;
  };

  // Configure jQuery to send CSRF header on same-origin requests
  $.ajaxSetup({
    beforeSend(xhr, settings) {
      const safeMethod = /^(GET|HEAD|OPTIONS|TRACE)$/i;
      if (!safeMethod.test(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
      }
    }
  });

  // Debounce
  const debounce = (fn, wait = 200) => {
    let timer = null;
    return function (...args) {
      const ctx = this;
      clearTimeout(timer);
      timer = setTimeout(() => fn.apply(ctx, args), wait);
    };
  };

  
  function buildPickedExerciseRow({ id, name, sets = 3, reps = 10 }) {
    const $li = $('<li/>', {
      class: 'list-group-item d-flex align-items-center',
      'data-id': id
    });

    const $name = $('<span/>', { class: 'picked-name flex-grow-1' }).text(name);
    const $sets = $('<input/>', {
      type: 'number',
      min: 1,
      class: 'form-control form-control-sm picked-sets mx-2',
      placeholder: 'Sets',
      value: sets,
      style: 'width:80px'
    });
    const $reps = $('<input/>', {
      type: 'number',
      min: 1,
      class: 'form-control form-control-sm picked-reps mx-2',
      placeholder: 'Reps',
      value: reps,
      style: 'width:80px'
    });
    const $remove = $('<button/>', {
      type: 'button',
      class: 'btn btn-sm btn-outline-danger remove-picked',
      'aria-label': 'Remove ' + name
    }).text('Remove');

    $li.append($name, $sets, $reps, $remove);
    return $li;
  }

  
  function showMessage($target, text) {
    $target.text(text);
  }

  // ---- Selectors --------------------------------------------------
  const $exercisesListing = $('#exercises-listing');
  const $wExercisesListing = $('#w-exercises-listing');
  const $pickedContainerSelector = '#picked-exercises';
  const $workoutsListing = $('#workouts-listing');
  const $createWorkoutForm = $('#create-workout-form');
  const $createWorkoutBtn = $('#create-workout-btn');
  const $createWorkoutMsg = $('#create-workout-msg');

  // ---- Selection / Edit -----------------------------------------
  $exercisesListing.on('click', 'li.list-group-item', function (e) {
    // ignore the search input row
    if ($(this).find('#search-input').length) return;

    e.preventDefault();

    const id = $(this).data('id');
    const name = $(this).data('name') || '';
    const bodypart = $(this).data('bodypart') || '';

    // populate hidden id and form fields
    $('#edit-id').val(id);
    $('#edit-name').val(name);
    $('#edit-body-part').val(bodypart);

    // visual cue
    $exercisesListing.find('.list-group-item').removeClass('active');
    const $item = $(this);

    $item.addClass('flash');
    setTimeout(() => $item.removeClass('flash'), 320);

    $('#edit-name').focus();
  });

  // ---- Pick exercise into workout handlers -------------------------------
  $wExercisesListing.on('click', 'li.list-group-item', function (e) {
    if ($(this).find('#search-input').length) return;

    e.preventDefault();

    const id = $(this).data('id');
    const name = $(this).data('name') || '';
    if (!name) return;

    // Ensure picked list exists
    let $picked = $( $pickedContainerSelector );
    if (!$picked.length) {
      $picked = $('<ul/>', { id: 'picked-exercises', class: 'list-group mt-3' })
        .insertAfter('#exercises-listing');
    }

    // Blink picked item
    const $src = $(this);
    $src.addClass('flash');
    setTimeout(() => $src.removeClass('flash'), 300);

    const $li = buildPickedExerciseRow({ id, name });
    $picked.append($li);
    
    $li[0].scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  });

  // Remove the picked item
  $doc.on('click', '#picked-exercises .remove-picked', function (e) {
    e.stopPropagation(); // avoid triggering parent clicks
    $(this).closest('li').remove();
  });

  // ---- Delete exercise confirmation -------------------------------------
  $('#delete-exercise-btn').on('click', function (e) {
    const ok = confirm('Are you sure you want to delete this exercise? This cannot be undone.');
    if (!ok) {
      e.preventDefault();
      return false;
    }

    return true;
  });

  // ---- Clear edit form --------------------------------------------------
  $('#clear-edit-btn').on('click', function () {
    $('#edit-id').val('');
    $('#edit-name').val('');
    $('#edit-body-part').val('');
    $('.list-group-item').removeClass('active');
  });


  // ---- Suggest -----------------------------
  // Suggest sender function
  function sendSuggest(query, url, targetSelector) {
    $.get(url, { suggestion: query })
      .done(function (data) {
        const $target = $(targetSelector);
        $target.empty().append(data);
      })
      .fail(function () {
        console.error('Suggest request failed for', url);
      });
  }

  
  $('#exercise-search-input').on('keyup', debounce(function () {
    const query = $(this).val();
  
    sendSuggest(query, '/fittrack/exercise_suggest/', '#exercises-listing');
    sendSuggest(query, '/fittrack/exercise_suggest/', '#w-exercises-listing');
  }, 200));

  $('#workout-search-input').on('keyup', debounce(function () {
    const query = $(this).val();
    sendSuggest(query, '/fittrack/workout_suggest/', '#workouts-listing');
  }, 200));

  // ---- Create workout ---------------------------
  $createWorkoutBtn.on('click', function () {
    const $btn = $(this);
    $createWorkoutMsg.empty();
    const workoutName = $('#workout-name').val().trim();

    if (!workoutName) {
      showMessage($createWorkoutMsg, 'Please enter a workout name.');
      return;
    }

    const $picked = $('#picked-exercises li[data-id]');
    if (!$picked.length) {
      showMessage($createWorkoutMsg, 'Add at least one exercise to the picked list.');
      return;
    }

    const exercise_ids = [];
    const sets = [];
    const reps = [];
    const orders = [];

    let validationError = false;

    $picked.each(function (index) {
      const $li = $(this);
      const exId = $li.data('id');
      const setVal = parseInt($li.find('.picked-sets').val(), 10) || 0;
      const repVal = parseInt($li.find('.picked-reps').val(), 10) || 0;

      if (!exId || setVal <= 0 || repVal <= 0) {
        $li.addClass('border border-danger');
        showMessage($createWorkoutMsg, 'Each picked exercise must have valid sets and reps (> 0).');
        validationError = true;
        return false;
      }

      exercise_ids.push(exId);
      sets.push(setVal);
      reps.push(repVal);
      orders.push(index + 1);
    });

    if (validationError) return;

    // Disable UI while request runs
    const originalLabel = $btn.text();
    $btn.prop('disabled', true).text('Creating…');

    // Build data
    const data = { name: workoutName };
    data['exercise_id[]'] = exercise_ids;
    data['sets[]'] = sets;
    data['reps[]'] = reps;
    data['order[]'] = orders;

    $.ajax({
      url: $createWorkoutForm.attr('action'),
      method: 'POST',
      data: data,
      traditional: true,
      success(resp) {
        if (resp && resp.success) {
          showMessage($createWorkoutMsg, 'Workout created (id: ' + resp.workout_id + ').');
          
          window.location.reload();
        } else {
          showMessage($createWorkoutMsg, resp && resp.error ? resp.error : 'Failed to create workout.');
        }
      },
      error(xhr) {
        let text = 'Server error while creating workout.';
        try {
          const json = JSON.parse(xhr.responseText);
          text = json.error || text;
        } catch (e) { /* ignore parse errors */ }
        showMessage($createWorkoutMsg, text);
      },
      complete() {
        $btn.prop('disabled', false).text(originalLabel);
      }
    });
  });

  // ---- Delete workout ---------------------------------------
  $workoutsListing.on('click', '.delete-workout', function (e) {
    e.preventDefault();
    e.stopPropagation();

    const $btn = $(this);
    const workoutId = $btn.data('id');
    const workoutName = $btn.closest('li').data('name') || '';

    if (!workoutId) return;

    if (!confirm('Delete workout "' + workoutName + '"? This will remove its exercises too.')) {
      return;
    }

    $btn.prop('disabled', true).text('Deleting…');

    
    const url = $createWorkoutForm.attr('action') || window.location.href;

    $.ajax({
      url,
      method: 'POST',
      data: { workout_id: workoutId, delete: '1' },
      success(resp) {
        if (resp && resp.success) {
          const $li = $workoutsListing.find('li[data-id="' + resp.workout_id + '"]').first();
          if ($li.length) {
            $li.fadeOut(200, function () { $(this).remove(); });

            if ($workoutsListing.find('li[data-id]').length === 0) {
              $workoutsListing.append('<li class="list-group-item"><em>No workouts found.</em></li>');
            }
          } else {
            window.location.reload();
          }
        } else {
          alert(resp && resp.error ? resp.error : 'Failed to delete workout.');
          $btn.prop('disabled', false).text('Delete');
        }
      },
      error(xhr) {
        let text = 'Server error while deleting workout.';
        try {
          const json = JSON.parse(xhr.responseText);
          text = json.error || text;
        } catch (e) { /* ignore */ }
        alert(text);
        $btn.prop('disabled', false).text('Delete');
      }
    });
  });


  $('.add-set-btn').click(function() {
      var exerciseId = $(this).data('exercise');
      var table = $('#table-' + exerciseId + ' tbody');
      var totalFormsInput = $('#id_exercise_' + exerciseId + '-TOTAL_FORMS');
      var totalForms = parseInt(totalFormsInput.val());

      // Clone empty row from last row
      var lastRow = table.find('tr:last');
      var newRow = lastRow.clone();

      // Clear input values
      newRow.find('input').each(function() {
          var name = $(this).attr('name');
          var newName = name.replace('-' + (totalForms - 1) + '-', '-' + totalForms + '-');
          $(this).attr('name', newName);
          $(this).attr('id', 'id_' + newName);
          $(this).val('');
          if ($(this).attr('type') === 'checkbox') {
              $(this).prop('checked', false);
          }
      });

      // Update set number
      newRow.find('td:first').text(totalForms + 1);

      // Append new row
      table.append(newRow);

      // Increment TOTAL_FORMS
      totalFormsInput.val(totalForms + 1);
  });

  
  
  

  $(function () {
    console.log('Fittrack UI loaded');
  });
})(jQuery);