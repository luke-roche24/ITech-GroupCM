import fittrack.models as m
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views import View

from .forms import EditExerciseForm, ExerciseForm, get_set_formset


class ExerciseView(LoginRequiredMixin, View):
    def get(self, request):
        exercise_list = m.Exercise.objects.filter(owner=request.user).order_by("name")
        form = ExerciseForm()
        edit_form = EditExerciseForm()

        context_dict = {
            "exercises": exercise_list,
            "add_exercise": form,
            "edit_exercise": edit_form,
        }
        return render(request, "fittrack/exercises.html", context_dict)

    def post(self, request):
        exercise_id = request.POST.get("exercise_id", "").strip()

        if exercise_id and "delete" in request.POST:
            exercise = get_object_or_404(m.Exercise, pk=exercise_id, owner=request.user)
            exercise.delete()
            return redirect(reverse("fittrack:exercises"))

        if exercise_id:
            exercise = get_object_or_404(m.Exercise, pk=exercise_id, owner=request.user)
            form = EditExerciseForm(request.POST, instance=exercise)
            if form.is_valid():
                form.save()
                return redirect(reverse("fittrack:exercises"))
            else:
                exercise_list = m.Exercise.objects.filter(owner=request.user).order_by("name")
                context_dict = {
                    "exercises": exercise_list,
                    "add_exercise": ExerciseForm(),
                    "edit_exercise": form,
                }
                return redirect(reverse("fittrack:exercises"))

        form = ExerciseForm(request.POST)

        if form.is_valid():
            exercise = form.save(commit=False)
            exercise.owner = request.user
            exercise.save()
            return redirect(reverse("fittrack:exercises"))

        exercise_list = m.Exercise.objects.filter(owner=request.user).order_by("name")
        context_dict = {
            "exercises": exercise_list,
            "add_exercise": form,
        }
        return render(request, "fittrack/exercises.html", context_dict)


class ExerciseSuggestionView(LoginRequiredMixin, View):
    def get(self, request):
        suggestion = request.GET.get("suggestion", "").strip()

        if suggestion:
            exercise_list = m.Exercise.objects.filter(
                owner=request.user, name__istartswith=suggestion
            ).order_by("name")
        else:
            exercise_list = m.Exercise.objects.filter(owner=request.user).order_by("name")

        return render(request, "fittrack/exercise_list_items.html", {"exercises": exercise_list})


def get_exercise_list(max_results=0, starts_with=""):
    exercise_list = []

    if starts_with:
        exercise_list = m.Exercise.objects.filter(name__istartswith=starts_with)

    if max_results > 0:
        if len(exercise_list) > max_results:
            exercise_list = exercise_list[:max_results]

    return exercise_list


class _DummyExerciseForFormset:
    def __init__(self, base_exercise, sets):
        self.sets = sets
        self.id = base_exercise.id
        self.name = base_exercise.name


def get_exercise_formset(request):
    exercise_id = request.GET.get("exercise_id")
    if not exercise_id:
        return JsonResponse({"error": "No exercise ID"}, status=400)

    exercise = get_object_or_404(m.Exercise, id=exercise_id, owner=request.user)

    # Keep the original behaviour: create a dummy object with the attributes
    # `get_set_formset` expects.
    dummy_exercise = _DummyExerciseForFormset(exercise, sets=1)

    FormSet = get_set_formset(dummy_exercise)
    formset = FormSet(prefix=f"new_exercise_{exercise.id}")

    html = render_to_string(
        "fittrack/exercise_formset_card.html",
        {
            "exercise": dummy_exercise,
            "formset": formset,
            "is_new": True,
        },
    )
    return JsonResponse({"html": html})

