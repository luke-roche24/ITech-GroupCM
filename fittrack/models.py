from django.db import models
from django.contrib.auth.models import User


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
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exercises')
    name = models.CharField(max_length=35)
    body_part = models.CharField(max_length=25)

    def __str__(self):
        return self.name


class Workout(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workouts')
    name = models.CharField(max_length=35)

    def __str__(self):
        return self.name


class WorkoutExercise(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name='workout_exercises')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    order = models.SmallIntegerField()
    sets = models.SmallIntegerField()
    reps = models.SmallIntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.workout.name} - {self.exercise.name}"


class Plan(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='plans')
    name = models.CharField(max_length=25)

    def __str__(self):
        return self.name


class PlanWorkout(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='plan_workouts')
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    day_index = models.SmallIntegerField()

    class Meta:
        ordering = ['day_index']

    def __str__(self):
        return f"{self.plan.name} - Day {self.day_index}"


class WorkoutSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.workout.name} ({self.date:%Y-%m-%d})"


class SetLog(models.Model):
    session = models.ForeignKey(WorkoutSession, on_delete=models.CASCADE, related_name='set_logs')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    set_num = models.SmallIntegerField()
    reps = models.SmallIntegerField()
    weight = models.DecimalField(max_digits=5, decimal_places=1)
    duration = models.IntegerField(default=0)
    failure = models.BooleanField(default=False)

    class Meta:
        ordering = ['set_num']

    def __str__(self):
        return f"Set {self.set_num}: {self.exercise.name}"


class IncrementSetting(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='increment_settings')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    increment = models.DecimalField(max_digits=4, decimal_places=1, default=2.5)

    class Meta:
        unique_together = ['user', 'exercise']

    def __str__(self):
        return f"{self.exercise.name}: +{self.increment}"


class Friendship(models.Model):
    user_a = models.ForeignKey(User, related_name='friendships_initiated', on_delete=models.CASCADE)
    user_b = models.ForeignKey(User, related_name='friendships_received', on_delete=models.CASCADE)
    status = models.BooleanField(default=False)

    class Meta:
        unique_together = ['user_a', 'user_b']

    def __str__(self):
        status_str = "Friends" if self.status else "Pending"
        return f"{self.user_a.username} - {self.user_b.username} ({status_str})"
