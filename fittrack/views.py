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


def index(request):
    if request.user.is_authenticated:
        return redirect('fittrack:dashboard')
    return render(request, 'fittrack/index.html')


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
def dashboard(request):
    context = {'username': request.user.username}
    return render(request, 'fittrack/dashboard.html', context)


@login_required
def current(request):
    return render(request, 'fittrack/current.html')


@login_required
def exercises(request):
    exercise_list = Exercise.objects.filter(owner=request.user).order_by('body_part', 'name')
    context = {'exercises': exercise_list}
    return render(request, 'fittrack/exercises.html', context)


@login_required
def friends(request):
    return render(request, 'fittrack/friends.html')


@login_required
def progress(request):
    return render(request, 'fittrack/progress.html')


@login_required
def workouts(request):
    return render(request, 'fittrack/workouts.html')


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
