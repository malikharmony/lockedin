from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import Profile
from jobs.models import JobApplication, JobPosting


class JobApplicationWorkflowTests(TestCase):
    def setUp(self):
        self.employer = get_user_model().objects.create_user(
            username='recruiter',
            email='recruiter@example.com',
            password='password123',
        )
        self.job_seeker = get_user_model().objects.create_user(
            username='applicant',
            email='applicant@example.com',
            password='password123',
        )

        Profile.objects.update_or_create(user=self.employer, defaults={'role': 'employer'})
        Profile.objects.update_or_create(user=self.job_seeker, defaults={'role': 'job_seeker'})

        self.job = JobPosting.objects.create(
            title='Senior Django Developer',
            description='Build the next generation of hosted services.',
            recruiter=self.employer,
            work_type='remote',
            required_skills='Django, Python, REST APIs',
            location='Boston, MA',
            visa_sponsorship=True,
            salary_min=125000,
            salary_max=160000,
            status='active',
        )

        self.application = JobApplication.objects.create(
            job=self.job,
            applicant=self.job_seeker,
            cover_letter='I am excited to apply for this role.',
            status='applied',
        )

    def test_applicant_can_view_application_status(self):
        self.client.login(username='applicant', password='password123')
        response = self.client.get(reverse('jobs.applications'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Senior Django Developer')
        self.assertContains(response, 'Applied')

    def test_employer_can_view_applicants_and_update_status(self):
        self.client.login(username='recruiter', password='password123')
        response = self.client.post(
            reverse('jobs.applicants', kwargs={'id': self.job.id}),
            {'application_id': self.application.id, 'status': 'review'},
            follow=True,
        )

        self.application.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.application.status, 'review')
        self.assertContains(response, 'Review')

    def test_employer_can_deny_applicant_and_close_status(self):
        self.client.login(username='recruiter', password='password123')
        response = self.client.post(
            reverse('jobs.applicants', kwargs={'id': self.job.id}),
            {'application_id': self.application.id, 'status': 'closed'},
            follow=True,
        )

        self.application.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.application.status, 'closed')
        self.assertContains(response, 'Closed')
