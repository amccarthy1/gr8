from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from grading.models import *
from django.contrib import auth
from django.contrib.auth import views
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .forms import ProfileForm


def view_home(request):
    return render(request, "index.html")

def login(request):

    if request.user.is_authenticated():
        return redirect("grading:home")

    if request.method == "POST":
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect(request.POST.get('next','grading:home'))
        else:
            return render(request, "login.html", {"login_successful": False})

    return render(request, "login.html")

def logout(request):

    if request.user.is_authenticated():
        auth.logout(request)
        return render(request, "index.html", {"logout_sucess": True})
    else:
        return redirect("grading:home")

def user_registration(request):

    if request.method == "POST":
        #create user
        #render
        pass

    profile_form = ProfileForm()

    return render(request, "user_registration.html", {"profile_form" : profile_form})


# View that lists all courses.
@login_required
def course_list(request):
    context = {
        'courses': Course.objects.all()
    }
    return render(request, "course_list.html", context)

@login_required
def course_info(request, course_id=0):
    c = get_object_or_404(Course, pk=course_id)
    context = {
        'course': c
    }
    return render(request, "course_info.html", context)

@login_required
def courses_enrolled(request):
    profile = request.user.profile
    if profile is None:
        raise Http404()

    my_enrolls = profile.enrolled_in_set.all()

    context = {
        'profile': profile,
        'enrolled_ins' : my_enrolls,
    }

    return render(request, "courses_enrolled.html", context)
