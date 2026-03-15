# populate_rango.py
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fittrack_project.settings')

import django
django.setup()

import fittrack.models as m
from django.utils import timezone
from django.contrib.auth import get_user_model


def populate():
    exercises = [
        {'id': 2, 'name': 'Bench Dumbbell Press', 'body_part': 'Chest'},
    ]

    users = [
        {'username': 'lukeroche', 'password': '1234'},
    ]

    # create/get a user (we return the user instance)
    user_data = users[0]
    u = add_user(user_data['username'], user_data['password'])

    # add exercises owned by the user
    for e in exercises:
        add_exercise(e['id'], u, e['name'], e['body_part'])

    print("Done populating.")

    


    


def add_exercise(eid, owner, name, body_part):
    """
    Create or get an Exercise. `owner` should be a User instance.
    Adjust the field name `ownerid` below to match your Exercise model's FK name
    (e.g. owner, ownerid, user, created_by, etc.).
    """
    # If owner field on Exercise is a FK called `ownerid`, use ownerid=owner.
    # If it's called `owner` or `user`, change the keyword below accordingly.
    e, created = m.Exercise.objects.get_or_create(
        id=eid,
        defaults={'ownerid': owner, 'name': name, 'body_part': body_part}
    )
    # Update fields in case the object existed but fields changed
    e.ownerid = owner
    e.name = name
    e.body_part = body_part
    e.save()
    return e

def add_user(username, password):
    """
    Create or get a Django auth user and set a hashed password.
    We don't forcibly set the user's ID here (let Django create it).
    """
    User = get_user_model()
    user, created = User.objects.get_or_create(username=username)
    # Always set the password using set_password (hashes it)
    user.set_password(password)
    user.save()
    return user



if __name__ == '__main__':
    print('Starting Rango population script...')
    populate()