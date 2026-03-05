from django.urls import path
from fittrack import views
app_name = 'fittrack'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('current/', views.current, name='current'),
    path('exercises/', views.exercises, name='exercises'),
    path('friends/', views.friends, name='friends'),
    path('progress/', views.progress, name='progress'),
    path('workouts/', views.workouts, name='workouts'),
    
]