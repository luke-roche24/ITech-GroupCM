from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class Page(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    url = models.URLField()
    views = models.ImageField(default=0)

    def __str__(self):
        return self.title

"""Each of the classes below this represent a table in the database that is
required for the program to work.
In each class, each variable represents an entity in the table.
e.g. A User has an id, a username and a password.
Tango with django chapter 5: 5.1 - 5.6
"""


class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=20)

    def __str__(self):
        return self.username

class Exercise(models.Model):
    id = models.AutoField(primary_key=True)
    ownerid = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=35)
    body_part = models.CharField(max_length=25)

    def __str__(self):
        return self.name
    
class Workout(models.Model):
    id = models.AutoField(primary_key=True)
    ownerid = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=35)

    def __str__(self):
        return self.name
    
class Friendship(models.Model):
    userid_a = models.ForeignKey(User, related_name='friendships_initiated', on_delete=models.CASCADE)
    userid_b = models.ForeignKey(User, related_name='friendships_received', on_delete=models.CASCADE)
    status = models.BooleanField(default=False)

class WorkoutSession(models.Model):
    id = models.AutoField(primary_key=True)
    userid = models.ForeignKey(User, on_delete=models.CASCADE)
    workoutid = models.ForeignKey(Workout, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

class SetLog(models.Model):
    id = models.AutoField(primary_key=True)
    sessionid = models.ForeignKey(WorkoutSession, on_delete=models.CASCADE)
    exerciseid = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    set_num = models.SmallIntegerField()
    reps = models.SmallIntegerField()
    weight = models.DecimalField(max_digits=5, decimal_places=1)
    duration = models.SmallIntegerField()
    failure = models.BooleanField()

class WorkoutExercise(models.Model):
    id = models.AutoField(primary_key=True)
    workoutid = models.ForeignKey(Workout, on_delete=models.CASCADE)
    exerciseid = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    order = models.SmallIntegerField()
    sets = models.SmallIntegerField()
    reps = models.SmallIntegerField()
        
