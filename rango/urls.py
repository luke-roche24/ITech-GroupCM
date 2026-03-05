from django.urls import path
from rango import views
app_name = 'rango'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('current/', views.current, name='current'),
    path('exercises/', views.exercises, name='exercises')
]