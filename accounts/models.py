from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = [
        ('job_seeker', 'Job Seeker'),
        ('employer', 'Employer'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='job_seeker')
    headline = models.CharField(max_length=255, blank=True, default='')
    about = models.TextField(blank=True, default='')
    education = models.TextField(blank=True, default='')
    experience = models.TextField(blank=True, default='')
    skills = models.TextField(blank=True, default='')

    def __str__(self):
        return f"{self.user.username}'s Profile"
