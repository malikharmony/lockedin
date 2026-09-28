from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from jobs.models import JobPosting


class JobFilterTests(TestCase):
    def setUp(self):
        self.employer = get_user_model().objects.create_user(
            username='recruiter',
            email='recruiter@example.com',
            password='password123',
        )

        JobPosting.objects.create(
            title='Senior Python Developer',
            description='Build APIs and backend systems.',
            recruiter=self.employer,
            work_type='remote',
            required_skills='Django, Python, APIs',
            location='Boston, MA',
            visa_sponsorship=True,
            salary_min=120000,
            salary_max=150000,
            status='active',
        )

        JobPosting.objects.create(
            title='UX Designer',
            description='Shape user experiences for our SaaS products.',
            recruiter=self.employer,
            work_type='in-person',
            required_skills='Figma, UX Research, Prototyping',
            location='Austin, TX',
            visa_sponsorship=False,
            salary_min=90000,
            salary_max=110000,
            status='active',
        )

    def test_filters_jobs_by_title_skills_location_salary_work_type_and_visa(self):
        response = self.client.get(
            reverse('jobs.index'),
            {
                'title': 'python',
                'skills': 'django',
                'location': 'boston',
                'salary_min': '100000',
                'salary_max': '140000',
                'work_type': 'remote',
                'visa_sponsorship': 'on',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Senior Python Developer')
        self.assertNotContains(response, 'UX Designer')

    def test_filters_jobs_by_location_without_visa(self):
        response = self.client.get(
            reverse('jobs.index'),
            {
                'location': 'austin',
                'work_type': 'in-person',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'UX Designer')
        self.assertNotContains(response, 'Senior Python Developer')
