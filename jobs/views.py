from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from jobs.models import JobPosting
from accounts.models import Profile
from django.shortcuts import get_object_or_404


def index(request):
    return render(request, 'jobs/index.html')

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