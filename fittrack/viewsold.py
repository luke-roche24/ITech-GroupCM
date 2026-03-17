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
from django.views.generic import ListView
from django.db.models import Prefetch
from .forms import ExerciseForm, EditExerciseForm, WorkoutForm, ChooseWorkoutForm, SetLogForm, get_set_formset
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.template.loader import render_to_string
import re
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from fittrack.models import Exercise, UserProfile, SECURITY_QUESTIONS
from fittrack.forms import (
    UserRegistrationForm, UserProfileForm,
    ForgotPasswordForm, SecurityAnswerForm, ResetPasswordForm,
)


class IndexView(View):
    def get(self, request):

        context_dict = {}
    
        return render(request, 'fittrack/index.html', context=context_dict)

@login_required
def dashboard(request):
    context = {'username': request.user.username}
    return render(request, 'fittrack/dashboard.html', context)

@login_required
def current(request):
    return render(request, 'fittrack/current.html')


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
            exercise.owner = User.objects.first()
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
                workout.owner = User.objects.first()
                #-------------------------------------
                workout.save()

                created_ids = []
                for ex in parsed:
                    exercise_obj = get_object_or_404(m.Exercise, id=ex['exercise_id'])
                   
                    #if exercise_obj.ownerid != request.user:
                    #    transaction.set_rollback(True)
                    #    return JsonResponse({'success': False, 'error': f'Permission denied for exercise id {ex["exercise_id"]}'}, status=403)

                    we = m.WorkoutExercise.objects.create(
                        workout=workout,
                        exercise=exercise_obj,
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

class LogWorkoutView(View):

    def get(self, request):

        context_dict = {
            'choose_workout': ChooseWorkoutForm(user=User.objects.first())
        }
        return render(request, 'fittrack/log_workout.html', context=context_dict)
    
    def post(self, request):
        form = ChooseWorkoutForm(request.POST, user=User.objects.first())

        if form.is_valid():
            selected_workout = form.cleaned_data['workout']
            print(selected_workout)
            return redirect('fittrack:log_workout_detail', workout_id=selected_workout.id)
        
        return render(request, 'fittrack/log_workout.html', {'choose_workout': form})
        

class LogWorkoutSetsView(View):

    def get(self, request, workout_id):
        workout = get_object_or_404(m.Workout, id=workout_id, owner=User.objects.first())
        exercises = m.WorkoutExercise.objects.filter(workout=workout).order_by('order')

        formsets = []
        for exercise in exercises:
            FormSet = get_set_formset(exercise)
            formset = FormSet(prefix=f'exercise_{exercise.id}')
            formsets.append((exercise, formset))

        context_dict = {
            'workout': workout,
            'exercises': exercises,
            'formsets': formsets,
        }

        return render(request, 'fittrack/log_workout_detail.html', context=context_dict)

    def post(self, request, workout_id):
        workout = get_object_or_404(m.Workout, id=workout_id, owner=User.objects.first())
        exercises = m.WorkoutExercise.objects.filter(workout=workout).order_by('order')

        session = m.WorkoutSession.objects.create(user=request.user, workout=workout)

        formsets = {}
        all_valid = True

        for exercise in exercises:
            FormSet = get_set_formset(exercise, True)
            formset = FormSet(request.POST, prefix=f'exercise_{exercise.id}')
            formsets[exercise.id] = formset
            if not formset.is_valid():
                all_valid = False

        if all_valid:
            for exercise in exercises:
                formset = formsets[exercise.id]
                for i, form in enumerate(formset):
                    data = form.cleaned_data

                    if not data.get('reps') or not data.get('weight'):
                        continue

                    m.SetLog.objects.create(
                        session=session,
                        exercise=exercise.exercise,
                        set_num=i+1,
                        reps=data['reps'],
                        weight=data['weight'],
                        failure=data.get('failure', False)
                    )
            return redirect('fittrack:log_workout')

        formsets_list = [(exercise, formsets[exercise.id]) for exercise in exercises]

        context_dict = {
            'workout': workout,
            'exercises': exercises,
            'formsets': formsets_list,
        }

        return render(request, 'fittrack/log_workout_detail.html', context=context_dict)

class RecentWorkoutsView(ListView):
    model = m.WorkoutSession
    template_name = 'fittrack/recent_workouts.html'
    context_object_name = 'sessions'

    def get_queryset(self):
        return (m.WorkoutSession.objects
                .filter(user=self.request.user)
                .select_related('workout')  # eager load the workout template
                .prefetch_related(
                    Prefetch(
                        'setlog_set',
                        queryset=m.SetLog.objects.select_related('exercise'),
                        to_attr='prefetched_sets'
                    )
                )
                .order_by('-date')[:5])
    



def get_exercise_formset(request):
    exercise_id = request.GET.get('exercise_id')
    if not exercise_id:
        return JsonResponse({'error': 'No exercise ID'}, status=400)
    
    exercise = get_object_or_404(m.Exercise, id=exercise_id, owner=request.user)
    
    # Create a dummy WorkoutExercise-like object to determine initial sets count
    # You can set a default, e.g., 1 set, or allow user to specify later.
    # Here we create a simple object with a 'sets' attribute.
    class DummyExercise:
        def __init__(self, sets):
            self.sets = sets
            self.id = exercise.id
            self.name = exercise.name
    
    dummy_exercise = DummyExercise(sets=1)  # or exercise.sets? but that's from WorkoutExercise, not Exercise.
    
    FormSet = get_set_formset(dummy_exercise)
    formset = FormSet(prefix=f'new_exercise_{exercise.id}')
    
    html = render_to_string('fittrack/exercise_formset_card.html', {
        'exercise': dummy_exercise,
        'formset': formset,
        'is_new': True,
    })
    return JsonResponse({'html': html})

@login_required
def friends(request):
    return render(request, 'fittrack/friends.html')

@login_required
def progress(request):
    return render(request, 'fittrack/progress.html')



def search(request):
    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            result_list = ['test 1', 'test 2', 'test 3']

    return render(request, 'fittrack/search.html', {'result_list': result_list})
# Create your views here.


def user_register(request):
    if request.user.is_authenticated:
        return redirect('fittrack:dashboard')
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to FitTrack, {user.username}!')
            return redirect('fittrack:dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'fittrack/register.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('fittrack:dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'fittrack:dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'fittrack/login.html')


@login_required
def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('fittrack:index')

def forgot_password(request):
    """3-step password reset: username → security question → new password."""
    step = request.session.get('reset_step', 1)
    reset_user_id = request.session.get('reset_user_id')

    # Step 1: Enter username
    if step == 1:
        if request.method == 'POST':
            form = ForgotPasswordForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                try:
                    user = User.objects.get(username=username)
                    profile = user.profile
                    request.session['reset_user_id'] = user.id
                    request.session['reset_step'] = 2
                    return redirect('fittrack:forgot_password')
                except (User.DoesNotExist, UserProfile.DoesNotExist):
                    messages.error(request, 'Username not found.')
        else:
            form = ForgotPasswordForm()
        return render(request, 'fittrack/forgot_password.html', {
            'step': 1, 'form': form,
        })

    # Step 2: Answer security question
    elif step == 2 and reset_user_id:
        try:
            user = User.objects.get(id=reset_user_id)
            profile = user.profile
        except (User.DoesNotExist, UserProfile.DoesNotExist):
            request.session.pop('reset_step', None)
            request.session.pop('reset_user_id', None)
            return redirect('fittrack:forgot_password')

        question_display = dict(SECURITY_QUESTIONS).get(profile.security_question, '')

        if request.method == 'POST':
            form = SecurityAnswerForm(request.POST)
            if form.is_valid():
                answer = form.cleaned_data['answer'].lower().strip()
                if answer == profile.security_answer:
                    request.session['reset_step'] = 3
                    return redirect('fittrack:forgot_password')
                else:
                    messages.error(request, 'Incorrect answer. Please try again.')
        else:
            form = SecurityAnswerForm()

        return render(request, 'fittrack/forgot_password.html', {
            'step': 2, 'form': form,
            'question': question_display, 'username': user.username,
        })

    # Step 3: Set new password
    elif step == 3 and reset_user_id:
        try:
            user = User.objects.get(id=reset_user_id)
        except User.DoesNotExist:
            request.session.pop('reset_step', None)
            request.session.pop('reset_user_id', None)
            return redirect('fittrack:forgot_password')

        if request.method == 'POST':
            form = ResetPasswordForm(request.POST)
            if form.is_valid():
                user.set_password(form.cleaned_data['new_password'])
                user.save()
                # Clean up session
                request.session.pop('reset_step', None)
                request.session.pop('reset_user_id', None)
                messages.success(request, 'Password reset successfully! Please log in.')
                return redirect('fittrack:login')
        else:
            form = ResetPasswordForm()

        return render(request, 'fittrack/forgot_password.html', {
            'step': 3, 'form': form, 'username': user.username,
        })

    # Fallback
    else:
        request.session.pop('reset_step', None)
        request.session.pop('reset_user_id', None)
        return redirect('fittrack:forgot_password')


@login_required
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('fittrack:profile')
    else:
        form = UserProfileForm(instance=user_profile)
    context = {'user_profile': user_profile, 'form': form}
    return render(request, 'fittrack/profile.html', context)

