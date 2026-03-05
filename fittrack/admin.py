from django.contrib import admin
import rango.models as m
# Register your models here.

admin.site.register(m.Category)
admin.site.register(m.Page)
admin.site.register(m.User)
admin.site.register(m.Exercise)
admin.site.register(m.Workout)
admin.site.register(m.WorkoutSession)
admin.site.register(m.Friendship)
admin.site.register(m.SetLog)
admin.site.register(m.WorkoutExercise)


