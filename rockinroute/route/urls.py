from django.urls import path, re_path
from . import views
from django.conf.urls import url

appname = 'route'

urlpatterns = [
    path('', views.index, name = 'index'),
    path('calculate/', views.calculate, name='calculate'),
    path('spotify/', views.spotify, name='spotify'),
    path('search/', views.search, name='search'),
    re_path(r'^results/(?P<album_id>\>[0-9A-Za-z]+)' r'(?P<start_location>\>[0-9A-Za-z\.\ \-]+)' r'(?P<end_location>\>[0-9A-Za-z\.\ \-]+)' r'(?P<city_state_str>\>\|\|.+\|\|)' r'(?P<artist_locations>\>[0-9A-Za-z\.\ \%]+)', views.results, name='results')
]