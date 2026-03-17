
from django.contrib import admin
from django.urls import path
from django.urls import include
from fittrack import views
from django.conf import settings
from django.conf.urls.static import static
from registration.backends.simple.views import RegistrationView
from django.urls import reverse

    
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('fittrack/', include('fittrack.urls')),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
