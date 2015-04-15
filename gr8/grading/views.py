from django.shortcuts import render, get_object_or_404, redirect
from grading.models import *
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import Http404


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
            if Profile.objects.filter(user=user).count() == 0:
                Profile.objects.create(user=user)
            return redirect(request.POST.get('next','grading:home'))
        else:
            return render(request, "login.html", {"login_failed": True})

    return render(request, "login.html")

def logout(request):

    if request.user.is_authenticated():
        auth.logout(request)
        return render(request, "index.html")
    else:
        return redirect("grading:home")


# View that lists all courses.
@login_required
def course_list(request):
    context = {
        'courses': Course.objects.all(),
        'header': "All Courses"
    }
    return render(request, "course_list.html", context)

@login_required
def course_list_current(request):
    context = {
        'courses': Course.get_current_courses(),
        'header': "Current Courses"
    }
    return render(request, "course_list.html", context)

@login_required
def course_info(request, course_id=0):
    c = get_object_or_404(Course, pk=course_id)
    profile = request.user.profile

    can_enroll = (profile is not None and profile.can_enroll and c.professor != profile)
    is_professor = (c.professor == profile)

    is_enrolled = False
    is_in_cart = False
    success = True
    if profile:
        #is_enrolled is true if there is a Enrolled_In w/ this student & course
        is_enrolled = len(Enrolled_In.objects.filter(course=c ,student=profile, is_enrolled=True)) > 0
        is_in_cart = len(Enrolled_In.objects.filter(course=c, student=profile, is_enrolled=False)) > 0
        #when user tries to enroll or add to bucket
        if can_enroll and request.method == "POST":
            if "enroll" in request.POST:
                success = profile.enroll_in(c)
                is_enrolled = success
            elif not is_enrolled and not is_in_cart and "cart" in request.POST:
                enrolled_in = Enrolled_In.objects.create(course=c, student=profile, is_enrolled=False)
                is_in_cart = True
            elif not is_enrolled and is_in_cart and "cart_remove" in request.POST:
                enrolled_in = Enrolled_In.objects.filter(course=c, student=profile, is_enrolled=False)
                enrolled_in.delete()
                is_in_cart = False
            elif is_enrolled and "drop" in request.POST:
                enrolled_in = Enrolled_In.objects.filter(course=c, student=profile, is_enrolled=True)
                enrolled_in.delete()
                is_enrolled = False

    context = {
        'course': c,
        'can_enroll' : can_enroll,
        'is_enrolled' : is_enrolled,
        'is_in_cart' : is_in_cart,
        'enroll_success' : success,
        'is_professor' : is_professor,
    }
    return render(request, "course_info.html", context)

@login_required
def courses_mine(request):
    profile = request.user.profile
    if profile is None:
        raise Http404()

    #get only current courses that the user is in
    enrolled_ins = profile.get_current_enrolled()

    #get current courses the user is the professor of
    professor_of = Course.get_current_courses().filter(professor=profile)

    context = {
        'request': request,
        'enrolled_ins' : enrolled_ins,
        'professor_of' : professor_of,
    }

    return render(request, "courses_mine.html", context)

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

@login_required
def schedule(request):
    profile = request.user.profile
    if profile is None:
        raise Http404()

    enrolled_ins = profile.get_current_enrolled()

    #make a list of json to be rendered as schedule items
    default_date = "2015-01-04"#first sunday of the year, don't be curious about this
    sessions = []
    for enrolled_in in enrolled_ins:
        #get all sessions for this course
        course_sessions = enrolled_in.course.get_sessions()

        #jsonify all course sessions
        for course_session in course_sessions:
            #grab the string of the title, startTime, and endTime
            title = str(course_session.course)
            startTime = course_session.start_time.strftime("%H:%M:%S")
            endTime = course_session.end_time.strftime("%H:%M:%S")
            #get the number day it is
            day = str(course_session.day_to_int())

            #format the json, day, star
            session = "{ title: '%s' , day: %s, startTime: '%s', endTime: '%s' }" % (title, day, startTime, endTime)
            sessions.append(session)

    return render(request, "my_schedule.html", {'sessions' : sessions})