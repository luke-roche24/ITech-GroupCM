from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User

# Create your models here.

SECURITY_QUESTIONS = [
    ('pet', 'What was the name of your first pet?'),
    ('school', 'What primary school did you attend?'),
    ('city', 'In what city were you born?'),
    ('food', 'What is your favourite food?'),
    ('friend', "What is your best friend's name?"),
]

class UserProfile(models.Model):
    """Extends Django's built-in User model with extra fields."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True)
    security_question = models.CharField(max_length=10, choices=SECURITY_QUESTIONS, default='pet')
    security_answer = models.CharField(max_length=100, default='')

    def __str__(self):
        return self.user.username


class Exercise(models.Model):
    NAME_MAX_LENGTH = 128

    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    body_part = models.CharField(max_length=25)

    def __str__(self):
        return self.name
    
class Workout(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=35)

    def __str__(self):
        return self.name

class WorkoutExercise(models.Model):
    id = models.AutoField(primary_key=True)
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    order = models.SmallIntegerField()
    sets = models.SmallIntegerField()
    reps = models.SmallIntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.workout.name} - {self.exercise.name}"
    

class WorkoutSession(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)


class SetLog(models.Model):
    id = models.AutoField(primary_key=True)
    session = models.ForeignKey(WorkoutSession, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    set_num = models.SmallIntegerField()
    reps = models.SmallIntegerField()
    weight = models.DecimalField(max_digits=5, decimal_places=1)
    failure = models.BooleanField()

    class Meta:
        ordering = ['set_num']

    def __str__(self):
        return f"Set {self.set_num}: {self.exercise.name}"
    



class PlannedWorkout(models.Model):

    DAYS_OF_WEEK = [
        (0, 'M'),
        (1, 'T'),
        (2, 'W'),
        (3, 'T'),
        (4, 'F'),
        (5, 'S'),
        (6, 'S'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='planned_workouts')
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    day = models.IntegerField(choices=DAYS_OF_WEEK)
    #order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['day']
        unique_together = ['user', 'day']

    def __str__(self):
        return f"{self.day}: {self.workout.name}"
    

class Friendship(models.Model):
    user_a = models.ForeignKey(User, related_name='friendships_initiated', on_delete=models.CASCADE)
    user_b = models.ForeignKey(User, related_name='friendships_received', on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['user_a', 'user_b']

    def __str__(self):
        status_str = "Friends" if self.status else "Pending"
        return f"{self.user_a.username} - {self.user_b.username} ({status_str})"

