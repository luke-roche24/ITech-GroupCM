from django.contrib import admin
import fittrack.models as m
# Register your models here.

admin.site.register(m.Exercise)
admin.site.register(m.Friendship)
admin.site.register(m.UserProfile)
admin.site.register(m.Workout)
admin.site.register(m.WorkoutSession)
admin.site.register(m.SetLog)
admin.site.register(m.WorkoutExercise)
