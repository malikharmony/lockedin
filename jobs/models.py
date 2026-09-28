from django.db import models
from django.conf import settings

# Create your models here.

class JobPosting(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    recruiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,
        related_name = 'job_postings'
    )
    work_type = models.CharField(max_length=255, choices=[
        ("in-person", "In-person"),
        ("hybrid","Hybrid"),
        ("remote","Remote")
        ])
    required_skills = models.TextField()
    location = models.CharField(max_length=255)
    date = models.DateField(auto_now_add=True)
    visa_sponsorship = models.BooleanField(default=False)
    salary_min = models.PositiveIntegerField()
    salary_max = models.PositiveIntegerField()
    status = models.CharField(max_length=50, choices=[
        ("active", "Active"),
        ("closed", "Closed"),
        ("removed", "Removed")],
        default="active")
    def __str__(self):
        return self.title