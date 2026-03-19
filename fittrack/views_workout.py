import fittrack.models as m
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views import View
from django.views.generic import ListView

from .forms import ChooseWorkoutForm, WorkoutForm, get_set_formset


class WorkoutView(LoginRequiredMixin, View):
    def get(self, request):
        workout_list = m.Workout.objects.filter(owner=request.user).order_by("name")
        exercise_list = m.Exercise.objects.filter(owner=request.user).order_by("name")

        context_dict = {
            "workouts": workout_list,
            "exercises": exercise_list,
            "workout_form": WorkoutForm(),
        }
        return render(request, "fittrack/workouts.html", context_dict)

    def post(self, request):
        if "delete" in request.POST and request.POST.get("workout_id"):
            workout_id = request.POST.get("workout_id")
            workout = get_object_or_404(m.Workout, pk=workout_id, owner=request.user)

            workout.delete()

            if request.is_ajax() or request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": True, "workout_id": int(workout_id)})
            return redirect("fittrack:workouts")

        exercise_ids = request.POST.getlist("exercise_id[]")
        if exercise_ids:
            form = WorkoutForm(request.POST)
            if not form.is_valid():
                errors = form.errors.get_json_data()
                return JsonResponse(
                    {"success": False, "error": "Invalid workout data", "form_errors": errors},
                    status=400,
                )

            sets_list = request.POST.getlist("sets[]")
            reps_list = request.POST.getlist("reps[]")
            order_list = request.POST.getlist("order[]")

            parsed = []
            try:
                for i, exid in enumerate(exercise_ids):
                    exid_int = int(exid)
                    sets_int = int(sets_list[i])
                    reps_int = int(reps_list[i])
                    order_int = int(order_list[i])
                    if sets_int <= 0 or reps_int <= 0:
                        return JsonResponse(
                            {"success": False, "error": "Sets and reps must be > 0"}, status=400
                        )
                    parsed.append(
                        {
                            "exercise_id": exid_int,
                            "sets": sets_int,
                            "reps": reps_int,
                            "order": order_int,
                        }
                    )
            except (ValueError, TypeError):
                return JsonResponse({"success": False, "error": "Invalid numeric values"}, status=400)

            with transaction.atomic():
                workout = form.save(commit=False)

                workout.owner = request.user
                workout.save()

                created_ids = []
                for ex in parsed:
                    try:
                        exercise_obj = m.Exercise.objects.get(id=ex["exercise_id"], owner=request.user)
                    except m.Exercise.DoesNotExist:
                        transaction.set_rollback(True)
                        return JsonResponse(
                            {"success": False, "error": f'Permission denied for exercise id {ex["exercise_id"]}'},
                            status=403,
                        )

                    we = m.WorkoutExercise.objects.create(
                        workout=workout,
                        exercise=exercise_obj,
                        order=ex["order"],
                        sets=ex["sets"],
                        reps=ex["reps"],
                    )
                    created_ids.append(we.id)

            workout_html = render_to_string(
                "fittrack/workout_list_items.html", {"workout": workout}, request=request
            )

            if request.is_ajax() or request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "success": True,
                        "workout_id": workout.id,
                        "created_items": created_ids,
                        "workout_html": workout_html,
                    }
                )

            return redirect("fittrack:workouts")


class WorkoutSuggestionView(LoginRequiredMixin, View):
    def get(self, request):
        suggestion = request.GET.get("suggestion", "").strip()

        if suggestion:
            workout_list = m.Workout.objects.filter(
                owner=request.user, name__istartswith=suggestion
            ).order_by("name")
        else:
            workout_list = m.Workout.objects.filter(owner=request.user).order_by("name")

        return render(request, "fittrack/workout_list_items.html", {"workouts": workout_list})


class LogWorkoutView(LoginRequiredMixin, View):
    def get(self, request):
        context_dict = {"choose_workout": ChooseWorkoutForm(user=request.user)}
        return render(request, "fittrack/log_workout.html", context=context_dict)

    def post(self, request):
        form = ChooseWorkoutForm(request.POST, user=request.user)

        if form.is_valid():
            selected_workout = form.cleaned_data["workout"]
            print(selected_workout)
            return redirect("fittrack:log_workout_detail", workout_id=selected_workout.id)

        return render(request, "fittrack/log_workout.html", {"choose_workout": form})


class LogWorkoutSetsView(LoginRequiredMixin, View):
    def get(self, request, workout_id):
        workout = get_object_or_404(m.Workout, id=workout_id, owner=request.user)
        exercises = m.WorkoutExercise.objects.filter(workout=workout).order_by("order")

        formsets = []
        for exercise in exercises:
            FormSet = get_set_formset(exercise)
            formset = FormSet(prefix=f"exercise_{exercise.id}")
            formsets.append((exercise, formset))

        context_dict = {
            "workout": workout,
            "exercises": exercises,
            "formsets": formsets,
        }
        return render(request, "fittrack/log_workout_detail.html", context=context_dict)

    def post(self, request, workout_id):
        workout = get_object_or_404(m.Workout, id=workout_id, owner=request.user)
        exercises = m.WorkoutExercise.objects.filter(workout=workout).order_by("order")

        session = m.WorkoutSession.objects.create(user=request.user, workout=workout)

        formsets = {}
        all_valid = True

        for exercise in exercises:
            FormSet = get_set_formset(exercise, True)
            formset = FormSet(request.POST, prefix=f"exercise_{exercise.id}")
            formsets[exercise.id] = formset
            if not formset.is_valid():
                all_valid = False

        if all_valid:
            for exercise in exercises:
                formset = formsets[exercise.id]
                for i, form in enumerate(formset):
                    data = form.cleaned_data
                    if not data.get("reps") or not data.get("weight"):
                        continue
                    m.SetLog.objects.create(
                        session=session,
                        exercise=exercise.exercise,
                        set_num=i + 1,
                        reps=data["reps"],
                        weight=data["weight"],
                        failure=data.get("failure", False),
                    )
            return redirect("fittrack:log_workout")

        formsets_list = [(exercise, formsets[exercise.id]) for exercise in exercises]

        context_dict = {
            "workout": workout,
            "exercises": exercises,
            "formsets": formsets_list,
        }
        return render(request, "fittrack/log_workout_detail.html", context=context_dict)


class RecentWorkoutsView(LoginRequiredMixin, ListView):
    model = m.WorkoutSession
    template_name = "fittrack/recent_workouts.html"
    context_object_name = "sessions"

    def get_queryset(self):
        return (
            m.WorkoutSession.objects.filter(user=self.request.user)
            .select_related("workout")
            .prefetch_related(
                Prefetch(
                    "setlog_set",
                    queryset=m.SetLog.objects.select_related("exercise")
                                             .order_by("exercise_id", "set_num"),
                    to_attr="prefetched_sets",
                )
            )
            .order_by("-date")[:5]
        )
