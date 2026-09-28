from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

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
    projects = models.TextField(blank=True, default='')
    location = models.CharField(blank=True, default='', max_length=255)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Report(models.Model):


    # self explanatory
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('under_review', 'Under review'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]

    # the reporter
    reporter = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='submitted_reports',
    )

    # what did they report
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='moderation_reports',
    )
    object_id = models.PositiveBigIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    reason = models.CharField(max_length=100)
    details = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True)
    # tells us who reviewed the report (an admin)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_reports',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('status', '-created_at')

    #stringify to the status and report about the target
    def __str__(self):
        target = self.content_object or f'{self.content_type} #{self.object_id}'
        return f'{self.get_status_display()} report about {target}'
