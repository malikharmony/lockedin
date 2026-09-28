from django.contrib import admin
from .models import JobPosting, JobApplication, JobReport

@admin.action(description="Remove reported job(s) from site")
def remove_reported_jobs(modeladmin, request, queryset):
    updated_jobs = 0
    for report in queryset:
        job = report.job
        if job.status != 'removed':
            job.status = 'removed'
            job.save()
            updated_jobs += 1
    queryset.update(status='action_taken')
    modeladmin.message_user(
        request,
        f"{queryset.count()} report(s) processed. {updated_jobs} job posting(s) marked as removed."
    )


@admin.action(description="Dismiss selected report(s)")
def dismiss_reports(modeladmin, request, queryset):
    queryset.update(status='dismissed')
    modeladmin.message_user(request, f"{queryset.count()} report(s) dismissed.")


@admin.action(description="Mark selected report(s) as reviewed")
def mark_as_reviewed(modeladmin, request, queryset):
    queryset.update(status='reviewed')
    modeladmin.message_user(request, f"{queryset.count()} report(s) marked as reviewed.")


@admin.register(JobReport)
class JobReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'job', 'reason', 'reporter', 'status', 'created_at')
    list_filter = ('status', 'reason', 'created_at')
    search_fields = ('job__title', 'reporter__username', 'details', 'admin_notes')
    readonly_fields = ('created_at',)
    actions = [remove_reported_jobs, dismiss_reports, mark_as_reviewed]
    fieldsets = (
        (None, {
            'fields': ('job', 'reporter', 'reason', 'details', 'created_at')
        }),
        ('Admin Actions', {
            'fields': ('status', 'admin_notes')
        }),
    )


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ('title', 'recruiter', 'location', 'work_type', 'status', 'date', 'reports_count')
    list_filter = ('status', 'work_type', 'visa_sponsorship', 'date')
    search_fields = ('title', 'description', 'location', 'required_skills', 'recruiter__username')

    def reports_count(self, obj):
        return obj.reports.count()
    reports_count.short_description = 'Reports'


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'applicant', 'status', 'submitted_at')
    list_filter = ('status', 'submitted_at')
    search_fields = ('job__title', 'applicant__username')

