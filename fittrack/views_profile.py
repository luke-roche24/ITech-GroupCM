import fittrack.models as m
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Max, Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View

from .forms import (
    AddToPlanForm,
    ChangePasswordForm,
    ChooseWorkoutForm,
    EditUserInfoForm,
    UserProfileForm,
)

def search(request):
    result_list = []
    if request.method == "POST":
        query = request.POST.get("query", "").strip()
        if query:
            result_list = ["test 1", "test 2", "test 3"]
    return render(request, "fittrack/search.html", {"result_list": result_list})


@login_required
def profile(request):
    user_profile, created = m.UserProfile.objects.get_or_create(user=request.user)
    photo_form = UserProfileForm(instance=user_profile)
    info_form = EditUserInfoForm(instance=request.user)
    password_form = ChangePasswordForm(user=request.user)

    if request.method == "POST":
        if "upload_photo" in request.POST:
            photo_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
            if photo_form.is_valid():
                photo_form.save()
                messages.success(request, "Profile picture updated.")
                return redirect("fittrack:profile")

        elif "update_info" in request.POST:
            info_form = EditUserInfoForm(request.POST, instance=request.user)
            if info_form.is_valid():
                info_form.save()
                messages.success(request, "Profile information updated.")
                return redirect("fittrack:profile")

        elif "change_password" in request.POST:
            password_form = ChangePasswordForm(request.POST, user=request.user)
            if password_form.is_valid():
                request.user.set_password(password_form.cleaned_data["new_password"])
                request.user.save()
                login(request, request.user)
                messages.success(request, "Password changed successfully.")
                return redirect("fittrack:profile")

    context = {
        "user_profile": user_profile,
        "form": photo_form,
        "info_form": info_form,
        "password_form": password_form,
    }
    return render(request, "fittrack/profile.html", context)


class CurrentPlanView(LoginRequiredMixin, View):
    def get(self, request):
        planned_workouts = (
            m.PlannedWorkout.objects.filter(user=request.user)
            .order_by("day")
            .select_related("workout")
            .prefetch_related(
                Prefetch(
                    "workout__workoutexercise_set",
                    queryset=m.WorkoutExercise.objects.select_related("exercise").order_by("order"),
                    to_attr="exercise_details",
                )
            )
        )
        days = m.PlannedWorkout.DAYS_OF_WEEK
        form = AddToPlanForm(user=request.user)

        schedule_by_day = []
        for day_num, day in days:
            workouts_for_day = [pw for pw in planned_workouts if pw.day == day_num]
            schedule_by_day.append(
                {"day_let": day, "day_num": day_num, "workouts": workouts_for_day}
            )

        context_dict = {
            "schedule_by_day": schedule_by_day,
            "form": form,
            "workouts": planned_workouts,
            "choose_workout": ChooseWorkoutForm(user=request.user),
        }

        return render(request, "fittrack/current.html", context=context_dict)

    def post(self, request):
        if "delete_planned_id" in request.POST:
            planned_id = request.POST.get("delete_planned_id")
            try:
                planned = m.PlannedWorkout.objects.get(id=planned_id, user=request.user)
                planned.delete()
            except m.PlannedWorkout.DoesNotExist:
                pass
            return redirect("fittrack:current")

        day_num = request.POST.get("day_num")

        if day_num:
            form = AddToPlanForm(request.POST, user=request.user)
            if form.is_valid():
                workout = form.cleaned_data["workout"]
                m.PlannedWorkout.objects.create(user=request.user, workout=workout, day=day_num)
                return redirect(reverse("fittrack:current"))

        form = ChooseWorkoutForm(request.POST, user=request.user)

        if form.is_valid():
            selected_workout = form.cleaned_data["workout"]
            return redirect(
                "fittrack:log_workout_detail", workout_id=selected_workout.id
            )

        return redirect(reverse("fittrack:current"))


class ProgressView(LoginRequiredMixin, View):
    def get(self, request):
        exercises = m.Exercise.objects.filter(owner=request.user).order_by("name")
        return render(request, "fittrack/progress.html", {"exercises": exercises})


class ProgressDataView(LoginRequiredMixin, View):
    def get(self, request):
        exercise_id = request.GET.get("exercise_id")

        if not exercise_id:
            return JsonResponse({"error": "Missing exercise_id"}, status=400)

        try:
            limit = int(request.GET.get("limit", 10))
        except (TypeError, ValueError):
            limit = 10

        limit = max(1, min(limit, 50))

        exercise = get_object_or_404(m.Exercise, pk=exercise_id, owner=request.user)

        base_qs = m.SetLog.objects.filter(session__user=request.user, exercise=exercise).select_related(
            "session"
        )

        per_session = (
            base_qs.values("session_id", "session__date").annotate(max_weight=Max("weight")).order_by(
                "-session__date"
            )
        )[:limit]

        per_session = list(per_session)[::-1]

        data_points = [
            {
                "session_id": row["session_id"],
                "date": row["session__date"].date().isoformat()
                if row["session__date"]
                else None,
                "max_weight": float(row["max_weight"]) if row["max_weight"] is not None else None,
            }
            for row in per_session
        ]

        pb_row = base_qs.aggregate(pb=Max("weight"))
        pb = pb_row.get("pb")

        last_trained_date = (
            base_qs.order_by("-session__date").values_list("session__date", flat=True).first()
        )

        pb_date = None
        if pb is not None:
            pb_date = (
                base_qs.filter(weight=pb)
                .order_by("-session__date")
                .values_list("session__date", flat=True)
                .first()
            )

        return JsonResponse(
            {
                "exercise": {"id": exercise.id, "name": exercise.name},
                "limit": limit,
                "points": data_points,
                "pb": float(pb) if pb is not None else None,
                "pb_date": pb_date.date().isoformat() if pb_date else None,
                "last_trained": last_trained_date.date().isoformat() if last_trained_date else None,
            }
        )

