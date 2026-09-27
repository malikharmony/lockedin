from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

# boi this is our report migration so things work

class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveBigIntegerField()),
                ('reason', models.CharField(max_length=100)),
                ('details', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('under_review', 'Under review'), ('resolved', 'Resolved'), ('dismissed', 'Dismissed')], default='pending', max_length=20)),
                ('admin_notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='moderation_reports', to='contenttypes.contenttype')),
                ('reporter', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='submitted_reports', to=settings.AUTH_USER_MODEL)),
                ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_reports', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ('status', '-created_at')},
        ),
    ]
