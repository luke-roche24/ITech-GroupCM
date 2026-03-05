from django.shortcuts import render
from django.http import HttpResponse
from fittrack.models import Exercise

def index(request):
    context_dict = {'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!'}
    return render(request, 'fittrack/index.html', context=context_dict)

# Create your views here.
def about(request):
    context_dict = {'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!'}
    return render(request, 'fittrack/about.html', context=context_dict)

def dashboard(request):
    context_dict = {'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!'}
    return render(request, 'fittrack/dashboard.html', context=context_dict)

def current(request):
    context_dict = {'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!'}
    return render(request, 'fittrack/current.html', context=context_dict)

def exercises(request):
    exercise_list = Exercise.objects.order_by('name')[:5]
    context_dict = {'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!'}
    context_dict['exercises'] = exercise_list
    return render(request, 'fittrack/exercises.html', context=context_dict)

def friends(request):
    context_dict = {'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!'}
    return render(request, 'fittrack/friends.html', context=context_dict)

def progress(request):
    context_dict = {'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!'}
    return render(request, 'fittrack/progress.html', context=context_dict)

def workouts(request):
    context_dict = {'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!'}
    return render(request, 'fittrack/workouts.html', context=context_dict)
