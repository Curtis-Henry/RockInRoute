from django.urls import path
from . import views

appname = 'route'

urlpatterns = [
    path('', views.index, name = 'index'),
    path('calculate/', views.calculate, name='calculate'),
    path('spotify/', views.spotify, name='spotify'),
    path('search/', views.search, name='search')
]