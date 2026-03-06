from django.urls import path
from fittrack import views
app_name = 'fittrack'

"""This file links each of the url paths to a view in the views.py file.
The url paths are words at the end of a url.
e.g. www.fittrack.com/dashboard/  --- Here the dashboard view would be 
displayed.

Tango with Django chapter 3.5
"""
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