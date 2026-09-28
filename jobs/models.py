from django.db import models
from django.conf import settings

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


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('review', 'Review'),
        ('interview', 'Interview'),
        ('offer', 'Offer'),
        ('closed', 'Closed'),
    ]

    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='job_applications',
    )
    cover_letter = models.TextField(blank=True, default='')
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')

    class Meta:
        unique_together = ('job', 'applicant')
        ordering = ('-submitted_at',)

    def __str__(self):
        return f"{self.applicant.username} applied for {self.job.title}"

    @property
    def status_label(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)


class JobReport(models.Model):
    REASON_CHOICES = [
        ('inappropriate', 'Inappropriate or Offensive Content'),
        ('spam', 'Spam, Scam, or Phishing'),
        ('misleading', 'Misleading or Fraudulent Information'),
        ('expired', 'No Longer Available / Expired'),
        ('other', 'Other Reason'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('reviewed', 'Reviewed'),
        ('dismissed', 'Dismissed'),
        ('action_taken', 'Action Taken (Job Removed)'),
    ]

    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='job_reports',
    )
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    details = models.TextField(blank=True, default='')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    admin_notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f"Report on {self.job.title} - {self.get_reason_display()}"