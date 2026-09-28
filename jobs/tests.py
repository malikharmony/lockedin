from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from jobs.models import JobPosting


class JobIndexViewTests(TestCase):
    def test_index_displays_active_jobs(self):
        user = get_user_model().objects.create_user(
            username='recruiter',
            password='password123',
        )

        JobPosting.objects.create(
            title='Senior Python Developer',
            description='Build and maintain Django APIs for internal tools.',
            recruiter=user,
            work_type='remote',
            required_skills='Django, Python, APIs',
            location='Austin, TX',
            visa_sponsorship=True,
            salary_min=120000,
            salary_max=150000,
            status='active',
        )

        response = self.client.get(reverse('jobs.index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Senior Python Developer')
        self.assertContains(response, 'Remote')
        self.assertContains(response, 'Austin, TX')
