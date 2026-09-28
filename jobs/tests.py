from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import Profile
from jobs.models import JobPosting


class ForYouRecommendationTests(TestCase):
    def setUp(self):
        self.applicant = get_user_model().objects.create_user(
            username='applicant',
            email='applicant@example.com',
            password='password123',
        )
        self.employer = get_user_model().objects.create_user(
            username='recruiter',
            email='recruiter@example.com',
            password='password123',
        )

        Profile.objects.update_or_create(user=self.applicant, defaults={'role': 'job_seeker', 'skills': 'Python Django APIs'})
        Profile.objects.update_or_create(user=self.employer, defaults={'role': 'employer'})

        JobPosting.objects.create(
            title='Senior Python Developer',
            description='Build core backend services.',
            recruiter=self.employer,
            work_type='remote',
            required_skills='Python, Django, REST APIs',
            location='Boston, MA',
            visa_sponsorship=True,
            salary_min=120000,
            salary_max=150000,
            status='active',
        )

        JobPosting.objects.create(
            title='UX Designer',
            description='Design product experiences for internal teams.',
            recruiter=self.employer,
            work_type='hybrid',
            required_skills='Figma, UX Research',
            location='Austin, TX',
            visa_sponsorship=False,
            salary_min=90000,
            salary_max=110000,
            status='active',
        )

    def test_for_you_shows_matching_jobs_based_on_profile_skills(self):
        self.client.login(username='applicant', password='password123')
        response = self.client.get(reverse('jobs.for_you'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Senior Python Developer')
        self.assertNotContains(response, 'UX Designer')

    def test_for_you_shows_empty_state_when_profile_has_no_matching_skills(self):
        self.applicant.profile.skills = 'Illustration Brand Design'
        self.applicant.profile.save()

        self.client.login(username='applicant', password='password123')
        response = self.client.get(reverse('jobs.for_you'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Personalized results will appear here once you update your profile.')
