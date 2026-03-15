from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)

    def __str__(self):
        return self.user.username


class Exercise(models.Model):
    NAME_MAX_LENGTH = 128

    id = models.AutoField(primary_key=True)
    ownerid = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=NAME_MAX_LENGTH)
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