from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='search.index'),
    path('candidates/', views.candidates, name='search.candidates')
]