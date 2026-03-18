from django import forms
from django.contrib.auth.models import User
from fittrack.models import Exercise, Workout, SetLog, UserProfile, PlannedWorkout
from django.contrib.auth.password_validation import validate_password
from fittrack.models import UserProfile, SECURITY_QUESTIONS

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

class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'id': 'workout-name', 'placeholder': 'Workout Name', 'maxlength': 35}),
        }


class ChooseWorkoutForm(forms.Form):
    workout = forms.ModelChoiceField(
        queryset=Workout.objects.none(),
        widget=forms.Select(attrs={'class': 'custom-select'})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['workout'].queryset = Workout.objects.filter(owner=user)

class SetLogForm(forms.ModelForm):
    reps = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1})
    )
    weight = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': 0.5})
    )
    to_failure = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = SetLog
        fields = ('reps', 'weight', 'failure')

def get_set_formset(exercise, zero=False):
    if zero:
        extra = 0
    else:
        extra = exercise.sets

    return forms.formset_factory(SetLogForm, extra=extra, can_delete=False)


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create a password',
        })
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password',
        }),
        label='Confirm Password',
    )
    security_question = forms.ChoiceField(
        choices=SECURITY_QUESTIONS,
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
    )
    security_answer = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your answer',
        }),
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your@email.com',
            }),
        }

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                security_question=self.cleaned_data['security_question'],
                security_answer=self.cleaned_data['security_answer'].lower().strip(),
            )
        return user


class ForgotPasswordForm(forms.Form):
    """Step 1: Enter username."""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username',
        }),
    )


class SecurityAnswerForm(forms.Form):
    """Step 2: Answer security question."""
    answer = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your answer',
        }),
    )


class ResetPasswordForm(forms.Form):
    """Step 3: Set new password."""
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'New password',
        }),
    )
    new_password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password',
        }),
    )

    def clean_new_password(self):
        password = self.cleaned_data.get('new_password')
        if password:
            validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_password')
        p2 = cleaned_data.get('new_password_confirm')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture']
        widgets = {
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }

class EditUserInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = False

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This username is already taken.")
        return username


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Current Password',
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='New Password',
    )
    new_password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Confirm New Password',
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if self.user and not self.user.check_password(old_password):
            raise forms.ValidationError("Current password is incorrect.")
        return old_password

    def clean_new_password(self):
        password = self.cleaned_data.get('new_password')
        if password:
            validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_password')
        p2 = cleaned_data.get('new_password_confirm')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("New passwords do not match.")
        return cleaned_data


class AddToPlanForm(forms.Form):
    workout = forms.ModelChoiceField(
        queryset=Workout.objects.none(),
        widget=forms.Select(attrs={'class': 'searchable-select'})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['workout'].queryset = Workout.objects.filter(owner=user)