from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from fittrack.models import UserProfile, Exercise, Workout, WorkoutExercise


class UserAuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        UserProfile.objects.create(user=self.user, security_question='pet', security_answer='dog')

    def test_register_page_loads(self):
        response = self.client.get(reverse('fittrack:register'))
        self.assertEqual(response.status_code, 200)

    def test_login_page_loads(self):
        response = self.client.get(reverse('fittrack:login'))
        self.assertEqual(response.status_code, 200)

    def test_login_valid_user(self):
        response = self.client.post(reverse('fittrack:login'), {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)

    def test_login_invalid_user(self):
        response = self.client.post(reverse('fittrack:login'), {
            'username': 'testuser',
            'password': 'wrongpass',
        })
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('fittrack:logout'))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('fittrack:dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_loads_when_logged_in(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('fittrack:dashboard'))
        self.assertEqual(response.status_code, 200)


class ExerciseTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        UserProfile.objects.create(user=self.user, security_question='pet', security_answer='dog')
        self.client.login(username='testuser', password='testpass123')

    def test_exercises_page_loads(self):
        response = self.client.get(reverse('fittrack:exercises'))
        self.assertEqual(response.status_code, 200)

    def test_add_exercise(self):
        response = self.client.post(reverse('fittrack:exercises'), {
            'name': 'Bench Press',
            'body_part': 'Chest',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Exercise.objects.filter(name='Bench Press', owner=self.user).exists())

    def test_edit_exercise(self):
        exercise = Exercise.objects.create(name='Squat', body_part='Legs', owner=self.user)
        response = self.client.post(reverse('fittrack:exercises'), {
            'exercise_id': exercise.id,
            'name': 'Back Squat',
            'body_part': 'Legs',
        })
        self.assertEqual(response.status_code, 302)
        exercise.refresh_from_db()
        self.assertEqual(exercise.name, 'Back Squat')

    def test_delete_exercise(self):
        exercise = Exercise.objects.create(name='Deadlift', body_part='Back', owner=self.user)
        response = self.client.post(reverse('fittrack:exercises'), {
            'exercise_id': exercise.id,
            'delete': 'true',
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Exercise.objects.filter(id=exercise.id).exists())


class ProfileTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        UserProfile.objects.create(user=self.user, security_question='pet', security_answer='dog')
        self.client.login(username='testuser', password='testpass123')

    def test_profile_page_loads(self):
        response = self.client.get(reverse('fittrack:profile'))
        self.assertEqual(response.status_code, 200)

    def test_update_username(self):
        response = self.client.post(reverse('fittrack:profile'), {
            'update_info': 'true',
            'username': 'newname',
            'email': '',
        })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'newname')

    def test_change_password(self):
        response = self.client.post(reverse('fittrack:profile'), {
            'change_password': 'true',
            'old_password': 'testpass123',
            'new_password': 'newpass456!Ab',
            'new_password_confirm': 'newpass456!Ab',
        })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass456!Ab'))

    def test_change_password_wrong_old(self):
        response = self.client.post(reverse('fittrack:profile'), {
            'change_password': 'true',
            'old_password': 'wrongpass',
            'new_password': 'newpass456!Ab',
            'new_password_confirm': 'newpass456!Ab',
        })
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('testpass123'))
