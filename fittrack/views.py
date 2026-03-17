from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from fittrack.models import Exercise, UserProfile, SECURITY_QUESTIONS, Friendship, WorkoutSession
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
    current_user = request.user

    search_results = None
    if request.method == "POST":
        if "search_user" in request.POST:
            query = request.POST.get("search_user")
            existing = Friendship.objects.filter(
                Q(user_a=current_user) | Q(user_b=current_user)
            ).values_list("user_a_id", "user_b_id")
            exclude_ids = {current_user.id}
            for a, b in existing:
                exclude_ids.add(a)
                exclude_ids.add(b)
            search_results = User.objects.filter(
                username__icontains=query
            ).exclude(id__in=exclude_ids)

        elif "add_friend" in request.POST:
            target_user = User.objects.get(id=request.POST.get("friend_id"))
            Friendship.objects.get_or_create(user_a=current_user, user_b=target_user, status=False)
            return redirect("fittrack:friends")

        elif "accept_friend" in request.POST:
            friendship = Friendship.objects.get(id=request.POST.get("request_id"))
            friendship.status = True
            friendship.save()
            return redirect("fittrack:friends")

    pending_requests = Friendship.objects.filter(user_b=current_user, status=False)

    friends_query = Friendship.objects.filter(
        (Q(user_a=current_user) | Q(user_b=current_user)) & Q(status=True)
    )
    confirmed_friends = []
    for f in friends_query:
        friend_obj = f.user_b if f.user_a == current_user else f.user_a
        recent = WorkoutSession.objects.filter(user=friend_obj).order_by("-date").first()
        confirmed_friends.append({"user": friend_obj, "recent": recent})

    context = {
        "pending_requests": pending_requests,
        "confirmed_friends": confirmed_friends,
        "search_results": search_results,
    }
    return render(request, "fittrack/friends.html", context)


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
