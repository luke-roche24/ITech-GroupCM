# populate_rango.py
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tango_with_django_project.settings')

import django
django.setup()

import rango.models as m
from django.utils import timezone


def populate():
    python_pages = [
        {'title': 'Official Python Tutorial', 'url': 'http://docs.python.org/3/tutorial/'},
        {'title': 'How To Think Like a Computer Scientist', 'url': 'http://www.greenteapress.com/thinkpython/'},
        {'title': 'A Python Tutorial (Korokithakis)', 'url': 'http://www.korokithakis.net/tutorials/python/'}
    ]

    django_pages = [
        {'title': 'Official Django Tutorial', 'url': 'https://docs.djangoproject.com/en/2.1/intro/tutorial01/'},
        {'title': 'DjangoRocks', 'url': 'http://www.djangorocks.com/'},
        {'title': 'How to Tango with Django', 'url': 'http://www.tangowithdjango.com/'}
    ]

    other_pages = [
        {'title': 'Bottle', 'url': 'http://bottlepy.org/docs/dev/'},
        {'title': 'Flask', 'url': 'http://flask.pocoo.org'}
    ]

    cats = {
        'Python': {'pages': python_pages},
        'Django': {'pages': django_pages},
        'OtherFrameworks': {'pages': other_pages}
    }

    for cat_name, cat_data in cats.items():
        c = add_cat(cat_name)
        for p in cat_data['pages']:
            add_page(c, p['title'], p['url'])

    # print out what we added
    for c in m.Category.objects.all():
        for p in m.Page.objects.filter(category=c):
            print(f'- {c.name}: {p.title} ({p.url})')


def add_page(cat, title, url, views=0):
    p, created = m.Page.objects.get_or_create(category=cat, title=title)
    p.url = url
    p.views = views
    p.save()
    return p


def add_cat(name):
    c, created = m.Category.objects.get_or_create(name=name)
    c.save()
    return c


if __name__ == '__main__':
    print('Starting Rango population script...')
    populate()