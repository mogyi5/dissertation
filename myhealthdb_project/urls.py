"""myhealthdb_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import include, path
from django.contrib import admin

from django.conf import settings
from django.conf.urls.static import static
# from registration.backends.default.views import RegistrationView
from myhealthdb import views

urlpatterns = [
    path('captcha/', include('captcha.urls')),
    path('myhealthdb/', include('myhealthdb.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('contact/', include('contact_form.urls')),
    path('select2/', include('django_select2.urls')),
    #path('search/', include('haystack.urls')),
    #path('accounts/signup/staff/',views.staff_signup, name='signup-staff'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
