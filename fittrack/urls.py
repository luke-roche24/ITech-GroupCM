from django.urls import path
from fittrack import views
app_name = 'fittrack'


urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    #path('about/', views.about, name='about'),
    #path('add_category/', views.add_category, name='add_category'),
    #path('category/<slug:category_name_slug>/add_page/',
    #     views.add_page, name='add_page'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('current/', views.current, name='current'),
    path('exercises/', views.ExerciseView.as_view(), name='exercises'),
    path('friends/', views.friends, name='friends'),
    path('progress/', views.progress, name='progress'),
    path('workouts/', views.workouts, name='workouts'),
    #path('register/', views.register, name='register'),
    #path('login/', views.user_login, name='login'),
    #path('restricted/', views.restricted, name='restricted'),
    #path('logout/', views.user_logout, name='logout'),
    path('search/', views.search, name='search'),
    #path('goto/', views.gotoview, name='goto'),
    path('suggest/', views.ExerciseSuggestionView.as_view(), name='suggest'),
    
]