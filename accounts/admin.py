from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BuiltInUserAdmin
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Profile, Report


class ProfileInline(admin.StackedInline):
    model = Profile
    extra = 0
    max_num = 1
    fieldsets = (
        ('Platform role', {'fields': ('role',)}),
        ('Professional profile', {
            'fields': ('headline', 'about', 'education', 'experience', 'skills'),
            'classes': ('collapse',),
        }),
    )


admin.site.unregister(User)


@admin.register(User)
class UserAdmin(BuiltInUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'get_role', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'profile__role')
    search_fields = ('username', 'email', 'first_name', 'last_name')

    @admin.display(description='Role', ordering='profile__role')
    def get_role(self, obj):
        try:
            return obj.profile.get_role_display()
        except Profile.DoesNotExist:
            return 'Not assigned'


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'headline')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email', 'headline', 'skills')


# ability to put reports under review
@admin.action(description='Mark selected reports as under review')
def mark_under_review(modeladmin, request, queryset):
    queryset.update(status='under_review')


# ability to resolve reports
@admin.action(description='Resolve selected reports')
def resolve_reports(modeladmin, request, queryset):
    queryset.update(
        status='resolved',
        reviewed_by=request.user,
        reviewed_at=timezone.now(),
    )

# ability to dismiss the report (when people try to report for idiotic reasons)
@admin.action(description='Dismiss selected reports')
def dismiss_reports(modeladmin, request, queryset):
    queryset.update(
        status='dismissed',
        reviewed_by=request.user,
        reviewed_at=timezone.now(),
    )

# our admin reporting abilities
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'status', 'reason', 'reporter', 'reported_object',
        'created_at', 'reviewed_by',
    )
    list_filter = ('status', 'content_type', 'created_at')
    search_fields = (
        'reason', 'details', 'admin_notes', 'reporter__username',
        'reporter__email', 'object_id',
    )
    readonly_fields = ('created_at', 'reviewed_at', 'reviewed_by', 'reported_object')
    actions = (mark_under_review, resolve_reports, dismiss_reports)
    date_hierarchy = 'created_at'
    list_per_page = 25
    fieldsets = (
        ('Report', {'fields': ('reporter', 'content_type', 'object_id', 'reported_object', 'reason', 'details')}),
        ('Review', {'fields': ('status', 'admin_notes', 'reviewed_by', 'reviewed_at')}),
        ('Metadata', {'fields': ('created_at',)}),
    )

    @admin.display(description='Reported object')
    def reported_object(self, obj):
        return str(obj.content_object or f'{obj.content_type} #{obj.object_id}')
