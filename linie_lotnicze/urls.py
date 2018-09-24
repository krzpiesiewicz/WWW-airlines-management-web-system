"""linie_lotnicze URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, re_path
from django.views.generic import RedirectView

from linie_lotnicze import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('flights/<int:row_no>/<int:rows_cnt>/', views.flights, name="flights"),
    path('flight/<int:id>/', views.flight, name="flight"),
    path('crews/', RedirectView.as_view(url='/static/crews.html', permanent=True), name='crew'),
    path('ajax/login/', views.login, name='login'),
    path('ajax/crews/', views.crews, name='crews'),
    path('ajax/save-crew/', views.save_crew, name='save_crew'),
    path('ajax/delete-crew/', views.delete_crew, name='delete_crew'),
    path('ajax/crew-members/', views.crew_members, name='crew_members'),
    path('ajax/save-member/', views.save_member, name='save_member'),
    path('ajax/delete-member/', views.delete_member, name='delete_member'),
    path('ajax/flights-ids/<int:rows_cnt>/', views.flights_ids, name='flights_ids'),
    path('ajax/flight-crew/', views.flight_crew, name='flight_crew'),
    path('ajax/save-flight/', views.save_flight, name='save_flight'),
    path('', views.main, name="main"),
    re_path(r'.*', views.error404, name='error404'),
]
