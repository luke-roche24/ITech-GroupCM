# populate_rango.py
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapp_project.settings')

import django
django.setup()

import fittrack.models as m
from django.utils import timezone


def populate():
    exercises = [
        {'id': '1', 'ownerid': '1', 'name': 'Bench Press', 'body_part': 'Chest'}
    ]

    users = [
        {'id': '1', 'username': 'lukeroche', 'password': '1234'}
    ]

    user = users[0]
    u = add_user(user['id'], user['username'], user['password'])

    for e in exercises:
        add_exercise(e['id'], u, e['name'], e['body_part'])

    


    # print out what we added
    #for e in m.Exercise.objects.all():
    #    add_exercise(e['id'], u, e['name'], e['body_part'])


def add_exercise(id, oid, name, body_part):
    e, created = m.Exercise.objects.get_or_create(id=id, ownerid=oid, name=name, body_part=body_part)
    e.id = id
    e.ownerid = oid
    e.name = name
    e.body_part = body_part
    e.save()
    return e

def add_user(id, name, pw):
    u, created = m.User.objects.get_or_create(id=id, username=name, password=pw)
    u.id = id
    u.username = name
    u.password = pw
    u.save()
    return u



if __name__ == '__main__':
    print('Starting Rango population script...')
    populate()