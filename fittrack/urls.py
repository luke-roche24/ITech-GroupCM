from django.urls import path
from fittrack import views

app_name = 'fittrack'

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.user_register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('current/', views.current, name='current'),
    path('exercises/', views.exercises, name='exercises'),
    path('friends/', views.friends, name='friends'),
    path('progress/', views.progress, name='progress'),
    path('workouts/', views.workouts, name='workouts'),
    path('profile/', views.profile, name='profile'),
]
