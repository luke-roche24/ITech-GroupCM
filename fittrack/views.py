from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
import fittrack.models as m
#from fittrack.forms import CategoryForm, PageForm
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
#from fittrack.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime
from fittrack.search import run_query
from django.views import View
from .forms import ExerciseForm, EditExerciseForm, WorkoutForm
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.template.loader import render_to_string


class IndexView(View):
    def get(self, request):

        context_dict = {}
    
        return render(request, 'fittrack/index.html', context=context_dict)

def dashboard(request):
    context_dict = {}
    return render(request, 'fittrack/dashboard.html', context=context_dict)

def current(request):
    context_dict = {}
    return render(request, 'fittrack/current.html', context=context_dict)

class ExerciseView(View):

    def get(self, request):
        exercise_list = m.Exercise.objects.order_by('name')
        form = ExerciseForm()
        edit_form = EditExerciseForm()

        context_dict = {
            'exercises': exercise_list,
            'add_exercise': form,
            'edit_exercise': edit_form,
        }

        return render(request, 'fittrack/exercises.html', context_dict)

    def post(self, request):
        exercise_id = request.POST.get('exercise_id', '').strip()
        
        if exercise_id and 'delete' in request.POST:
            exercise = get_object_or_404(m.Exercise, pk=exercise_id)
            exercise.delete()
            return redirect(reverse('fittrack:exercises'))
        
        if exercise_id:
            exercise = get_object_or_404(m.Exercise, pk=exercise_id)
            form = EditExerciseForm(request.POST, instance=exercise)
            if form.is_valid():
                form.save()
                return redirect(reverse('fittrack:exercises'))
            else:
                exercise_list = m.Exercise.objects.order_by('name')
                context_dict = {
                    'exercises': exercise_list,
                    'add_exercise': ExerciseForm(),
                    'edit_exercise': form,
                }
                return redirect(reverse('fittrack:exercises'))
            

        form = ExerciseForm(request.POST)

        if form.is_valid():
            exercise = form.save(commit=False)
            #---------Temporary-------------------
            exercise.ownerid = User.objects.first()
            #-------------------------------------
            exercise.save()
            
            return redirect(reverse('fittrack:exercises'))
        
        exercise_list = m.Exercise.objects.order_by('name')

        context_dict = {
            'exercises': exercise_list,
            'add_exercise': form
        }
        
        return render(request, 'fittrack/exercises.html', context_dict)


class WorkoutView(View):
    
    def get(self, request):
        workout_list = m.Workout.objects.order_by('name')
        exercise_list = m.Exercise.objects.order_by('name')

        context_dict = {
            'workouts': workout_list,
            'exercises': exercise_list,
            'workout_form': WorkoutForm(),
        }

        return render(request, 'fittrack/workouts.html', context_dict)
    
    def post(self, request):

        
        if 'delete' in request.POST and request.POST.get('workout_id'):
            workout_id = request.POST.get('workout_id')
            
            workout = get_object_or_404(m.Workout, pk=workout_id)

            # ensure owner matches current user
            #if workout.ownerid != request.user:
                # permission denied
            #    if request.is_ajax() or request.headers.get('x-requested-with') == 'XMLHttpRequest':
            #        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
            #    return HttpResponseForbidden('Permission denied')

            
            workout.delete()

            
            if request.is_ajax() or request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'workout_id': int(workout_id)})
            return redirect('fittrack:workouts')

        exercise_ids = request.POST.getlist('exercise_id[]')
        if exercise_ids:
            form = WorkoutForm(request.POST)
            if not form.is_valid():
                errors = form.errors.get_json_data()
                return JsonResponse({'success': False, 'error': 'Invalid workout data', 'form_errors': errors}, status=400)
            

            sets_list = request.POST.getlist('sets[]')
            reps_list = request.POST.getlist('reps[]')
            order_list = request.POST.getlist('order[]')

            
            #if not (len(exercise_ids) == len(sets_list) == len(reps_list) == len(order_list)):
            #    return JsonResponse({'success': False, 'error': 'Mismatched exercise arrays'}, status=400)

            
            parsed = []
            try:
                for i, exid in enumerate(exercise_ids):
                    exid_int = int(exid)
                    sets_int = int(sets_list[i])
                    reps_int = int(reps_list[i])
                    order_int = int(order_list[i])
                    if sets_int <= 0 or reps_int <= 0:
                        return JsonResponse({'success': False, 'error': 'Sets and reps must be > 0'}, status=400)
                    parsed.append({'exercise_id': exid_int, 'sets': sets_int, 'reps': reps_int, 'order': order_int})
            except (ValueError, TypeError):
                return JsonResponse({'success': False, 'error': 'Invalid numeric values'}, status=400)

           
            with transaction.atomic():
                workout = form.save(commit=False)
                #---------Temporary-------------------
                workout.ownerid = User.objects.first()
                #-------------------------------------
                workout.save()

                created_ids = []
                for ex in parsed:
                    exercise_obj = get_object_or_404(m.Exercise, id=ex['exercise_id'])
                   
                    #if exercise_obj.ownerid != request.user:
                    #    transaction.set_rollback(True)
                    #    return JsonResponse({'success': False, 'error': f'Permission denied for exercise id {ex["exercise_id"]}'}, status=403)

                    we = m.WorkoutExercise.objects.create(
                        workoutid=workout,
                        exerciseid=exercise_obj,
                        order=ex['order'],
                        sets=ex['sets'],
                        reps=ex['reps']
                    )
                    created_ids.append(we.id)

           
            workout_html = render_to_string('fittrack/workout_list_items.html', {'workout': workout}, request=request)

            
            if request.is_ajax() or request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'workout_id': workout.id, 'created_items': created_ids, 'workout_html': workout_html})

           
            return redirect('fittrack:workouts')
    



def workouts(request):
    context_dict = {}
    return render(request, 'fittrack/workouts.html', context=context_dict)

class ExerciseSuggestionView(View):
    def get(self, request):
        suggestion = request.GET.get('suggestion', '').strip()

        if suggestion:
            exercise_list = m.Exercise.objects.filter(name__istartswith=suggestion).order_by('name')
        else:
            
            exercise_list = m.Exercise.objects.order_by('name')

        
        return render(request, 'fittrack/exercise_list_items.html', {'exercises': exercise_list})


def get_exercise_list(max_results=0, starts_with=''):
    exercise_list = []

    if starts_with:
        exercise_list = m.Exercise.objects.filter(name__istartswith=starts_with)
    
    if max_results > 0:
        if len(exercise_list) > max_results:
            exercise_list = exercise_list[:max_results]
    
    return exercise_list

class WorkoutSuggestionView(View):
    def get(self, request):
        suggestion = request.GET.get('suggestion', '').strip()

        if suggestion:
            workout_list = m.Workout.objects.filter(name__istartswith=suggestion).order_by('name')
        else:
            
            workout_list = m.Workout.objects.order_by('name')

        
        return render(request, 'fittrack/workout_list_items.html', {'workouts': workout_list})



def friends(request):
    context_dict = {}
    return render(request, 'fittrack/friends.html', context=context_dict)

def progress(request):
    context_dict = {}
    return render(request, 'fittrack/progress.html', context=context_dict)



def search(request):
    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            result_list = ['test 1', 'test 2', 'test 3']

    return render(request, 'fittrack/search.html', {'result_list': result_list})
# Create your views here.
"""
class AddExerciseView(View):
    template_name = 'fittrack/add_exercise.html'

    #@method_decorator(login_required)
    def get(self, request):
        form = ExerciseForm()
        return render(request, self.template_name, {'form': form})
    
    #@method_decorator(login_required)
    def post(self, request):
        form = ExerciseForm(request.POST)
        if form.is_valid():
            temp_user = User.objects.first()
            exercise = form.save(commit=False)   # don't write to DB yet
            exercise.ownerid = temp_user      # set the FK to current user
            exercise.save()
            return redirect(reverse('fittrack:exercises'))
        else:
            print(form.errors)
        return render(request, self.template_name, {'form': form})
"""

