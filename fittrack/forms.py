from django import forms
from django.contrib.auth.models import User
from fittrack.models import Exercise, UserProfile

# We could add these forms to views.py, but it makes sense to split them off into their own file.

class ExerciseForm(forms.ModelForm):

    class Meta:
        model = Exercise
        fields = ('name', 'body_part')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'body_part': forms.TextInput(attrs={'class': 'form-control'}),
        }

class EditExerciseForm(forms.ModelForm):

    class Meta:
        model = Exercise
        fields = ('name', 'body_part')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'id': 'edit-name', 'name': 'name'}),
            'body_part': forms.TextInput(attrs={'class': 'form-control', 'id': 'edit-body-part', 'name': 'body_part'})
        }