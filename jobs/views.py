from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from jobs.models import JobPosting, JobApplication
from accounts.models import Profile
from django.shortcuts import get_object_or_404


def index(request):
    jobs = JobPosting.objects.filter(status='active').order_by('-date')

    title = (request.GET.get('title') or '').strip()
    skills = (request.GET.get('skills') or '').strip()
    location = (request.GET.get('location') or '').strip()
    salary_min = request.GET.get('salary_min', '').strip()
    salary_max = request.GET.get('salary_max', '').strip()
    work_type = (request.GET.get('work_type') or '').strip()
    visa_sponsorship = request.GET.get('visa_sponsorship')

    if title:
        jobs = jobs.filter(title__icontains=title)
    if skills:
        jobs = jobs.filter(required_skills__icontains=skills)
    if location:
        jobs = jobs.filter(location__icontains=location)
    if salary_min:
        try:
            jobs = jobs.filter(salary_max__gte=int(salary_min))
        except ValueError:
            pass
    if salary_max:
        try:
            jobs = jobs.filter(salary_min__lte=int(salary_max))
        except ValueError:
            pass
    if work_type in ['in-person', 'hybrid', 'remote']:
        jobs = jobs.filter(work_type=work_type)
    if visa_sponsorship == 'on':
        jobs = jobs.filter(visa_sponsorship=True)

    template_data = {
        'title': 'Job Discovery | LockedIn',
        'jobs': jobs,
        'filters': {
            'title': title,
            'skills': skills,
            'location': location,
            'salary_min': salary_min,
            'salary_max': salary_max,
            'work_type': work_type,
            'visa_sponsorship': visa_sponsorship,
        },
    }
    return render(request, 'jobs/index.html', context={'template_data': template_data})


@login_required
def for_you(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if profile.role != 'job_seeker':
        messages.error(request, 'This page is only for job seekers.')
        return redirect('home.index')

    user_skills = {
        skill.strip().lower()
        for skill in (profile.skills or '').replace(',', ' ').split()
        if skill.strip()
    }

    jobs = JobPosting.objects.filter(status='active').order_by('-date')
    recommended_jobs = []

    if user_skills:
        for job in jobs:
            job_skills = {
                skill.strip().lower()
                for skill in (job.required_skills or '').replace(',', ' ').split()
                if skill.strip()
            }
            if user_skills & job_skills:
                recommended_jobs.append(job)

    template_data = {
        'title': 'For You | LockedIn',
    }

    return render(request, 'jobs/for_you.html', {
        'template_data': template_data,
        'jobs': recommended_jobs,
        'has_profile_skills': bool(user_skills),
    })


def detail(request, id):
    job = get_object_or_404(JobPosting, id=id, status='active')
    template_data = {
        'title': f'{job.title} | LockedIn',
    }

    return render(request, 'jobs/detail.html', {
        'template_data': template_data,
        'job': job,
        'is_applied': request.user.is_authenticated and request.user.job_applications.filter(job=job).exists(),
    })


@login_required
def apply(request, id):
    job = get_object_or_404(JobPosting, id=id, status='active')
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if profile.role != 'job_seeker':
        messages.error(request, 'Only job seekers can apply to positions.')
        return redirect('jobs.detail', id=job.id)

    cover_letter = (request.POST.get('cover_letter', '') or '').strip()

    application, created = JobApplication.objects.get_or_create(
        job=job,
        applicant=request.user,
        defaults={'cover_letter': cover_letter, 'status': 'applied'},
    )

    if not created:
        application.cover_letter = cover_letter or application.cover_letter
        application.status = 'applied'
        application.save()

    if cover_letter:
        application.cover_letter = cover_letter
        application.save()

    messages.success(request, 'Your profile information has been sent to the employer.')
    return redirect('jobs.detail', id=job.id)


@login_required
def applications(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if profile.role != 'job_seeker':
        messages.error(request, 'This page is only for applicants.')
        return redirect('home.index')

    applications = JobApplication.objects.filter(
        applicant=request.user
    ).select_related('job', 'job__recruiter').order_by('-submitted_at')

    template_data = {
        'title': 'My Applications | LockedIn',
    }

    return render(request, 'jobs/applications.html', {
        'template_data': template_data,
        'applications': applications,
    })


@login_required
def applicants(request, id):
    job = get_object_or_404(JobPosting, id=id, recruiter=request.user)

    if request.method == 'POST':
        application_id = request.POST.get('application_id')
        status = request.POST.get('status', '').strip()

        if application_id:
            application = get_object_or_404(job.applications, id=application_id)
            valid_statuses = ['applied', 'review', 'interview', 'offer', 'closed']

            if status in valid_statuses:
                application.status = status
                application.save()
                if status == 'closed':
                    messages.success(request, f'{application.applicant.username} was denied and marked as closed.')
                else:
                    messages.success(request, f'{application.applicant.username} status updated to {application.status_label}.')
            else:
                messages.error(request, 'Invalid application status.')

        return redirect('jobs.applicants', id=job.id)

    applications = job.applications.select_related('applicant').order_by('-submitted_at')
    template_data = {
        'title': f'Applicants for {job.title} | LockedIn',
    }

    return render(request, 'jobs/applicants.html', {
        'template_data': template_data,
        'job': job,
        'applications': applications,
    })

@login_required
def create_job(request):
    template_data = {
        "title" : "Post a Job | LockedIn"
    }

    is_employer = Profile.objects.filter(
        user=request.user,
        role='employer',
    ).exists()

    if not is_employer:
        messages.error(request, 'Only employers can post jobs.')
        return redirect('home.index')

    if request.method == 'POST':
        title = request.POST.get('title','').strip()
        description = request.POST.get('description','').strip()
        location = request.POST.get('location','').strip()
        work_type = request.POST.get('work_type','').strip()
        visa_sponsorship = 'visa_sponsorship' in request.POST
        required_skills = request.POST.get('required_skills', '').strip()
        try:
            salary_min = int(request.POST.get('salary_min',''))
            salary_max = int(request.POST.get('salary_max',''))
        except ValueError:
            messages.error(request, 'Salaries must be valid whole numbers')
            return render(
                request,
                'jobs/job_form.html',
                context={"template_data" : template_data}
            )
        if not all([title, description, location, required_skills, work_type]):
            messages.error(request, 'All fields must be completed')
            return render(
                request,
                'jobs/job_form.html',
                context={"template_data" : template_data}
            )
        if not work_type in ["in-person", "hybrid", "remote"]:
            messages.error(request, 'Work type must be in-person, hybrid, or remote')
            return render(
                request,
                'jobs/job_form.html',
                context={"template_data" : template_data}
            )
        if salary_min > 99999999 or salary_max > 99999999:
            messages.error(request, 'Salaries must not exceed limit')
            return render(
                request,
                'jobs/job_form.html',
                context={"template_data" : template_data}
            )
        if salary_min < 0 or salary_max < 0:
            messages.error(request, 'Salaries cannot be negative')
            return render(
                request,
                'jobs/job_form.html',
                context={"template_data" : template_data}
            )
        if salary_min > salary_max:
            messages.error(request, 'Minimum salary cannot be greater than the maximum salary')
            return render(
                request,
                'jobs/job_form.html',
                context={"template_data" : template_data}
            )

        job = JobPosting()
        job.title = title
        job.description = description
        job.location = location
        job.work_type = work_type
        job.required_skills = required_skills
        job.salary_min = salary_min
        job.salary_max = salary_max
        job.visa_sponsorship = visa_sponsorship
        job.recruiter = request.user
        job.save()

        messages.success(
            request,
            'Job posting created successfully.',
        )
        return redirect('jobs.my_jobs')


    return render(request, 'jobs/job_form.html',
                  context={"template_data" : template_data})


@login_required
def my_jobs(request):
    is_employer = Profile.objects.filter(
        user=request.user,
        role='employer',
    ).exists()

    if not is_employer:
        messages.error(request, 'Only employers can post jobs.')
        return redirect('home.index')

    jobs = JobPosting.objects.filter(
        recruiter=request.user
    ).order_by('-date')

    template_data = {
        "title" : "My Postings | LockedIn",
        "jobs" : jobs
    }

    return render(request, "jobs/my_jobs.html", context={"template_data" : template_data})


@login_required
def edit_job(request, id):
    is_employer = Profile.objects.filter(
        user=request.user,
        role='employer',
    ).exists()

    if not is_employer:
        messages.error(request, 'Only employers can post jobs.')
        return redirect('home.index')

    job = get_object_or_404(
        JobPosting,
        id=id,
        recruiter=request.user,
    )

    if job.status == 'removed':
        messages.error(
            request,
            'A removed job posting cannot be edited.',
        )
        return redirect('jobs.my_jobs')

    template_data = {
        "title" : "Edit Job | LockedIn"
    }

    if request.method == 'POST':
        title = request.POST.get('title','').strip()
        description = request.POST.get('description','').strip()
        location = request.POST.get('location','').strip()
        work_type = request.POST.get('work_type','').strip()
        visa_sponsorship = 'visa_sponsorship' in request.POST
        required_skills = request.POST.get('required_skills', '').strip()
        status = request.POST.get('status', '').strip()
        try:
            salary_min = int(request.POST.get('salary_min',''))
            salary_max = int(request.POST.get('salary_max',''))
        except ValueError:
            messages.error(request, 'Salaries must be valid whole numbers')
            return render(
                request,
                'jobs/job_form.html',
                context={"template_data" : template_data, "job" : job}
            )

        if status not in ["active", "closed"]:
            messages.error(request, 'Status must be active or closed')
            return render(
                request,
                'jobs/job_form.html',
                context={"template_data" : template_data, "job" : job}
            )

        if not all([title, description, location, required_skills, work_type]):
            messages.error(request, 'All fields must be completed')
            return render(
                request,
                'jobs/job_form.html',
                context={"template_data" : template_data, "job" : job}
            )
        if not work_type in ["in-person", "hybrid", "remote"]:
            messages.error(request, 'Work type must be in-person, hybrid, or remote')
            return render(
                request,
                'jobs/job_form.html',
                context={"template_data" : template_data, "job" : job}
            )
        if salary_min > 99999999 or salary_max > 99999999:
            messages.error(request, 'Salaries must not exceed limit')
            return render(
                request,
                'jobs/job_form.html',
                context={"template_data" : template_data, "job" : job}
            )
        if salary_min < 0 or salary_max < 0:
            messages.error(request, 'Salaries cannot be negative')
            return render(
                request,
                'jobs/job_form.html',
                context={"template_data" : template_data, "job" : job}
            )
        if salary_min > salary_max:
            messages.error(request, 'Minimum salary cannot be greater than the maximum salary')
            return render(
                request,
                'jobs/job_form.html',
                context={"template_data" : template_data, "job" : job}
            )

        job.title = title
        job.description = description
        job.location = location
        job.work_type = work_type
        job.required_skills = required_skills
        job.salary_min = salary_min
        job.salary_max = salary_max
        job.visa_sponsorship = visa_sponsorship
        job.status = status
        job.save()

        messages.success(
            request,
            'Job posting edited successfully.',
        )
        return redirect('jobs.my_jobs')



    return render(request, 'jobs/job_form.html', context={
        "template_data" : template_data,
        'job' : job
        })