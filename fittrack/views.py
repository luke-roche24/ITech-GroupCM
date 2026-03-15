from django.shortcuts import render
from django.http import HttpResponse
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
from .forms import ExerciseForm, EditExerciseForm
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


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


class ExerciseSuggestionView(View):
    def get(self, request):
        suggestion = request.GET.get('suggestion', '').strip()

        if suggestion:
            exercise_list = m.Exercise.objects.filter(name__istartswith=suggestion).order_by('name')
        else:
            # optionally return nothing or full list when no suggestion
            exercise_list = m.Exercise.objects.order_by('name')

        # Render only the li fragments
        return render(request, 'fittrack/exercise_list_items.html', {'exercises': exercise_list})


def get_exercise_list(max_results=0, starts_with=''):
    exercise_list = []

    if starts_with:
        exercise_list = m.Exercise.objects.filter(name__istartswith=starts_with)
    
    if max_results > 0:
        if len(exercise_list) > max_results:
            exercise_list = exercise_list[:max_results]
    
    return exercise_list

def friends(request):
    context_dict = {}
    return render(request, 'fittrack/friends.html', context=context_dict)

def progress(request):
    context_dict = {}
    return render(request, 'fittrack/progress.html', context=context_dict)

def workouts(request):
    context_dict = {}
    return render(request, 'fittrack/workouts.html', context=context_dict)

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

