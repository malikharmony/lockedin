from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='jobs.index'),
    path('create/', views.create_job, name='jobs.create'),
    path('mine/', views.my_jobs, name='jobs.my_jobs'),
    path('<int:id>/edit/', views.edit_job, name='jobs.edit'),
]