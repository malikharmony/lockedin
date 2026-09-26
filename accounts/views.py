from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile

def index(request):
    if request.user.is_authenticated:
        return redirect('accounts.profile', username=request.user.username)
    return redirect('accounts.login')

def signup(request):
    if request.user.is_authenticated:
        return redirect('accounts.profile', username=request.user.username)

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        role = request.POST.get('role', 'job_seeker')

        if not username or not email or not password:
            messages.error(request, 'Please fill in all required fields.')
            template_data = {'title': 'Sign Up | LockedIn'}
            return render(request, 'accounts/signup.html', {'template_data': template_data})

        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, f'Username "{username}" is already taken. Please choose another.')
            template_data = {'title': 'Sign Up | LockedIn'}
            return render(request, 'accounts/signup.html', {'template_data': template_data})

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'An account with this email already exists.')
            template_data = {'title': 'Sign Up | LockedIn'}
            return render(request, 'accounts/signup.html', {'template_data': template_data})

        user = User.objects.create_user(username=username, email=email, password=password)
        Profile.objects.create(user=user, role=role)

        messages.success(request, 'Account created successfully! Please sign in.')
        return redirect('accounts.login')

    template_data = {'title': 'Sign Up | LockedIn'}
    return render(request, 'accounts/signup.html', {'template_data': template_data})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts.profile', username=request.user.username)

    if request.method == 'POST':
        identifier = (
            request.POST.get('login_identifier', '').strip()
            or request.POST.get('email', '').strip()
            or request.POST.get('username', '').strip()
        )
        password = request.POST.get('password', '')

        user_obj = User.objects.filter(username__iexact=identifier).first()
        if not user_obj:
            user_obj = User.objects.filter(email__iexact=identifier).first()

        if user_obj:
            authenticated_user = authenticate(request, username=user_obj.username, password=password)
            if authenticated_user is not None:
                login(request, authenticated_user)

                profile, _ = Profile.objects.get_or_create(user=authenticated_user)
                if profile.headline or authenticated_user.first_name:
                    return redirect('accounts.profile', username=authenticated_user.username)
                
                return redirect('accounts.edit_profile')

        messages.error(request, 'Invalid username/email or password.')

    template_data = {'title': 'Sign In | LockedIn'}
    return render(request, 'accounts/login.html', {'template_data': template_data})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home.index')

@login_required(login_url='accounts.login')
def edit_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        headline = request.POST.get('headline', '').strip()
        about = request.POST.get('about', '').strip()
        education = request.POST.get('education', '').strip()
        experience = request.POST.get('experience', '').strip()
        skills = request.POST.get('skills', '').strip()

        if username and username.lower() != request.user.username.lower():
            if User.objects.filter(username__iexact=username).exists():
                messages.error(request, f'Username "{username}" is already taken.')
                template_data = {'title': 'Edit Your Profile | LockedIn'}
                return render(request, 'accounts/edit_profile.html', {
                    'template_data': template_data,
                    'profile': profile,
                })
            request.user.username = username

        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.save()

        profile.headline = headline
        profile.about = about
        profile.education = education
        profile.experience = experience
        profile.skills = skills
        profile.save()

        messages.success(request, 'Your profile has been saved!')
        return redirect('accounts.profile', username=request.user.username)

    template_data = {'title': 'Edit Your Profile | LockedIn'}
    return render(request, 'accounts/edit_profile.html', {
        'template_data': template_data,
        'profile': profile,
    })

def user_profile(request, username):
    user = get_object_or_404(User, username__iexact=username)
    profile, _ = Profile.objects.get_or_create(user=user)

    full_name = user.get_full_name()
    if not full_name:
        full_name = user.username

    template_data = {
        'title': f"{full_name} | LockedIn",
    }

    is_owner = request.user.is_authenticated and request.user == user

    return render(request, 'accounts/profile.html', {
        'template_data': template_data,
        'profile_user': user,
        'profile': profile,
        'full_name': full_name,
        'is_owner': is_owner,
    })