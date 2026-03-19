from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

from fittrack.models import SECURITY_QUESTIONS, UserProfile

from .forms import (
    ForgotPasswordForm,
    ResetPasswordForm,
    SecurityAnswerForm,
    UserRegistrationForm,
)

# Function to handle user registration and redirection
def user_register(request):
    if request.user.is_authenticated:
        return redirect("fittrack:dashboard")
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to FitTrack, {user.username}!")
            return redirect("fittrack:dashboard")
    else:
        form = UserRegistrationForm()
    return render(request, "fittrack/register.html", {"form": form})

# Function to handle user login authentication
def user_login(request):
    if request.user.is_authenticated:
        return redirect("fittrack:dashboard")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get("next", "fittrack:dashboard")
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "fittrack/login.html")


@login_required
def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("fittrack:index")


def forgot_password(request):
    """3-step password reset: username → security question → new password."""

    step = request.session.get("reset_step", 1)
    reset_user_id = request.session.get("reset_user_id")

    # Step 1: Enter username
    if step == 1:
        if request.method == "POST":
            form = ForgotPasswordForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data["username"]
                try:
                    user = User.objects.get(username=username)
                    profile = user.profile
                    request.session["reset_user_id"] = user.id
                    request.session["reset_step"] = 2
                    return redirect("fittrack:forgot_password")
                except (User.DoesNotExist, UserProfile.DoesNotExist):
                    messages.error(request, "Username not found.")
        else:
            form = ForgotPasswordForm()

        return render(request, "fittrack/forgot_password.html", {"step": 1, "form": form})

    # Step 2: Answer security question
    if step == 2 and reset_user_id:
        try:
            user = User.objects.get(id=reset_user_id)
            profile = user.profile
        except (User.DoesNotExist, UserProfile.DoesNotExist):
            request.session.pop("reset_step", None)
            request.session.pop("reset_user_id", None)
            return redirect("fittrack:forgot_password")

        question_display = dict(SECURITY_QUESTIONS).get(profile.security_question, "")

        if request.method == "POST":
            form = SecurityAnswerForm(request.POST)
            if form.is_valid():
                answer = form.cleaned_data["answer"].lower().strip()
                if answer == profile.security_answer:
                    request.session["reset_step"] = 3
                    return redirect("fittrack:forgot_password")
                messages.error(request, "Incorrect answer. Please try again.")
        else:
            form = SecurityAnswerForm()

        return render(
            request,
            "fittrack/forgot_password.html",
            {"step": 2, "form": form, "question": question_display, "username": user.username},
        )

    # Step 3: Set new password
    if step == 3 and reset_user_id:
        try:
            user = User.objects.get(id=reset_user_id)
        except User.DoesNotExist:
            request.session.pop("reset_step", None)
            request.session.pop("reset_user_id", None)
            return redirect("fittrack:forgot_password")

        if request.method == "POST":
            form = ResetPasswordForm(request.POST)
            if form.is_valid():
                user.set_password(form.cleaned_data["new_password"])
                user.save()
                request.session.pop("reset_step", None)
                request.session.pop("reset_user_id", None)
                messages.success(request, "Password reset successfully! Please log in.")
                return redirect("fittrack:login")
        else:
            form = ResetPasswordForm()

        return render(
            request,
            "fittrack/forgot_password.html",
            {"step": 3, "form": form, "username": user.username},
        )

    # Fallback
    request.session.pop("reset_step", None)
    request.session.pop("reset_user_id", None)
    return redirect("fittrack:forgot_password")

