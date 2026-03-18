from django.urls import path
from fittrack import views
app_name = 'fittrack'


urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('register/', views.user_register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('current/', views.CurrentPlanView.as_view(), name='current'),
    path('exercises/', views.ExerciseView.as_view(), name='exercises'),
    path('friends/', views.friends, name='friends'),
    path('progress/', views.progress, name='progress'),
    path('workouts/', views.WorkoutView.as_view(), name='workouts'),
    path('search/', views.search, name='search'),
    path('exercise_suggest/', views.ExerciseSuggestionView.as_view(), name='e_suggest'),
    path('workout_suggest/', views.WorkoutSuggestionView.as_view(), name='w_suggest'),
    path('log_workout/', views.LogWorkoutView.as_view(), name='log_workout'),
    path('log_workout/<int:workout_id>/', views.LogWorkoutSetsView.as_view(), name='log_workout_detail'),
    path('recent-workouts/', views.RecentWorkoutsView.as_view(), name='recent_workouts'),
    path('get-exercise-formset/', views.get_exercise_formset, name='get_exercise_formset'),
    path('profile/', views.profile, name='profile'),
]