from django.contrib import admin
from fittrack.models import (
    UserProfile, Exercise, Workout, WorkoutExercise,
    Plan, PlanWorkout, WorkoutSession, SetLog,
    IncrementSetting, Friendship,
)

admin.site.register(UserProfile)
admin.site.register(Exercise)
admin.site.register(Workout)
admin.site.register(WorkoutExercise)
admin.site.register(Plan)
admin.site.register(PlanWorkout)
admin.site.register(WorkoutSession)
admin.site.register(SetLog)
admin.site.register(IncrementSetting)
admin.site.register(Friendship)
