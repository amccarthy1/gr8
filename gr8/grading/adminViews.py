from grading.models import *
from .decorators import staff_required
from .forms import *
from django.shortcuts import render


@staff_required
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

    if request.user.is_superuser:
        user_form = SuperUserForm()
    else:
        user_form = UserForm()

    context = {"profile_form" : profile_form, "user_form" : user_form}

    return render(request, "user_registration.html", context)


@staff_required
def room_creation(request):

    roomList = Room.objects.all()

    if request.method == "POST":
        room_form = RoomForm(request.POST)

        if room_form.is_valid():
            room = room_form.save()
            room.save()

            roomList = Room.objects.all()
            room_form = RoomForm()
            return render(request, "room_creation.html", {"room_form" : room_form,"rooms" : roomList,
                "success" : True})

        else:
            return render(request, "room_creation.html", {"room_form" : room_form,"rooms" : roomList,
                "failure" : True})

    room_form = RoomForm()
    context = {"room_form" : room_form,"rooms" : roomList,}
    return render(request, "room_creation.html", context)


@staff_required
def create_course(request):

    if request.method == "POST":
        course_form = CourseForm(request.POST)
        code = Course_Code.objects.get_or_create(code=request.POST['code'])[0]

        if course_form.is_valid():
            course = course_form.save(commit=False)
            course.course_code = code
            course.save()

            course_form = CourseForm()
            return render(request, "course_creation.html", {"course_form": course_form, "success": True})

        else:
            return render(request, "course_creation.html", {"course_form": course_form, "failure": True})

    course_form = CourseForm()
    context = {"course_form" : course_form}
    return render(request, "course_creation.html", context)

@staff_required
def term_creation(request):

    termList = Term.objects.all()

    if request.method == "POST":
        term_form = TermForm(request.POST)

        if term_form.is_valid():
            term = term_form.save(commit=False)

            term.year = request.POST["end_date_year"]

            for existingTerm in termList:
                if str(term.season) == str(existingTerm.season) and str(term.year) == str(existingTerm.year):
                    return render(request, "term_creation.html", {"term_form": term_form, "failure": True, "terms":termList})

            term.save()
            termList = Term.objects.all()

            term_form = TermForm()
            return render(request, "term_creation.html", {"term_form": term_form, "success": True, "terms":termList})

        else:
            return render(request, "term_creation.html", {"term_form": term_form, "failure": True, "terms":termList})

    term_form = TermForm()
    context = {"term_form" : term_form, "terms":termList}
    return render(request, "term_creation.html", context)

@staff_required
def create_course_code(request):
    course_code_form = None
    created = None
    if (request.method == "POST"):
        course_code_form = CourseCodeForm(request.POST)
        if course_code_form.is_valid():
            code = course_code_form.save()
            created = code.code
        else:
            context = {"course_code_form" : course_code_form}
            return render(request, "course_code_creation.html", context)
    course_code_form = CourseCodeForm()
    context = {"course_code_form" : course_code_form, "created": created}
    return render(request, "course_code_creation.html", context)
