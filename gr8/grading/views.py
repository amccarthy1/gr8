from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from grading.models import *
from django.contrib import auth
from django.contrib.auth import views
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .forms import ProfileForm, UserForm, RoomForm
from django.contrib.admin.views.decorators import staff_member_required



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
        return render(request, "index.html")
    else:
        return redirect("grading:home")

def user_registration(request):

    if request.method == "POST":
        profile_form = ProfileForm(request.POST)
        user_form = UserForm(request.POST)

        if user_form.is_valid():
            django_user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = django_user
            profile.save()

            profile_form = ProfileForm()
            user_form = UserForm()
            return render(request, "user_registration.html", {"profile_form" : profile_form, "user_form" : user_form, 
                "success" : True})

        else:
            return render(request, "user_registration.html", {"profile_form" : profile_form, "user_form" : user_form, 
                "failure" : True})

    profile_form = ProfileForm()
    user_form = UserForm()

    context = {"profile_form" : profile_form, "user_form" : user_form}

    return render(request, "user_registration.html", context)


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

    my_enrolls = profile.enrolled_in_set.filter(is_enrolled=True)

    context = {
        'profile': profile,
        'enrolled_ins' : my_enrolls,
    }

    return render(request, "courses_enrolled.html", context)

@login_required
def shopping_bag(request):
    profile = request.user.profile
    if profile is None:
        raise Http404()

    if request.method == "POST":
        my_cart_courses = profile.enrolled_in_set.filter(is_enrolled=False)
        for enrolled_in in my_cart_courses:
            enrolled_in.is_enrolled = True
            enrolled_in.save()

    my_cart_courses = profile.enrolled_in_set.filter(is_enrolled=False)

    context = {
        'profile' : profile,
        'cart_courses' : my_cart_courses,
    }

    return render(request, "shopping_cart.html", context)

@staff_member_required
def room_creation(request):

    roomList = Room.objects.all()
    print(roomList)

    if request.method == "POST":
        room_form = RoomForm(request.POST)

        if room_form.is_valid():
            room = room_form.save()
            room.save()

            room_form = RoomForm()
            return render(request, "room_creation.html", {"room_form" : room_form,"rooms" : roomList,
                "success" : True})

        else:
            return render(request, "room_creation.html", {"room_form" : room_form,"rooms" : roomList,
                "failure" : True})

    room_form = RoomForm()
    context = {"room_form" : room_form,"rooms" : roomList,}
    return render(request, "room_creation.html", context)
