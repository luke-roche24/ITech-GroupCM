
from .views_basic import IndexView, dashboard
from .views_exercise import (
    ExerciseSuggestionView,
    ExerciseView,
    get_exercise_formset,
    get_exercise_list,
)
from .views_workout import (
    LogWorkoutSetsView,
    LogWorkoutView,
    RecentWorkoutsView,
    WorkoutSuggestionView,
    WorkoutView,
)
from .views_social import friends
from .views_account import forgot_password, user_login, user_logout, user_register
from .views_profile import (
    CurrentPlanView,
    ProgressDataView,
    ProgressView,
    profile,
    search,
)
