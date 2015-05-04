from .models import *
from .decorators import staff_required
from .forms import *
from django.forms.models import inlineformset_factory
from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError

@login_required
def course_grade(request, course_id=0, profile_id=0):

    profile = request.user.profile

    if profile is None:
        raise Http404()

    # try to get the course, if the correct professor is not the logged in profile it will 404
    c = get_object_or_404(Course.get_current_courses(), pk=course_id, professor=profile)

    enrolled_ins = Enrolled_In.objects.filter(course=c,is_enrolled=True)
    #this should make students without grades first, then subsort by last name, first name
    enrolled_ins = enrolled_ins.extra(select={
        'grade_is_null' : 'grade IS NULL',
        },
        order_by=['grade_is_null', 'student__user__last_name', 'student__user__first_name']
    )

    forms = []
    if request.method == "POST":
        #save all the forms!
        forms = [GradeForm(request.POST, prefix=str(x), instance=Enrolled_In()) for x in range(0,len(enrolled_ins))]
        for i in range(0,len(forms)):
            if forms[i].is_valid():
                enrolled_in = forms[i].save(commit=False)
                enrolled_ins[i].grade = enrolled_in.grade
                enrolled_ins[i].save()

    else:
        forms = [GradeForm(prefix=str(x), instance=enrolled_ins[x]) for x in range(0,len(enrolled_ins))]

    #create a list of stuff
    grade_items = []
    for i in range(0,len(enrolled_ins)):
        grade_items.append((enrolled_ins[i],forms[i]))

    context = {
        "grade_items": grade_items,
        "course" : c,
    }
    return render(request, "course_grade.html", context)



@staff_required
def user_registration(request):

    if request.method == "POST":
        profile_form = ProfileForm(request.POST)
        user_form = UserForm(request.POST)

        if user_form.is_valid():
            django_user = user_form.save()

            if "is_staff" in request.POST:
                django_user.is_staff = True
                django_user.save()

            profile = profile_form.save(commit=False)
            profile.user = django_user
            profile.save()

            profile_form = ProfileForm()

            if request.user.is_superuser:
                user_form = SuperUserForm()
            else:
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
    formset = None
    CourseCodeInlineFormSet = inlineformset_factory(Course_Code, Prereq, fk_name="prereq_course", can_delete=False)
    created = None
    if (request.method == "POST"):
        course_code_form = CourseCodeForm(request.POST)
        formset = CourseCodeInlineFormSet(request.POST)
        if formset.is_valid() and course_code_form.is_valid():
            dummy = course_code_form.save(commit=False) #don't commit yet
            formset = CourseCodeInlineFormSet(request.POST, instance=dummy)
            code = course_code_form.save()
            formset.save()
            created = code.code
        else:
            context = {"formset" : formset, "ccf": course_code_form}
            return render(request, "course_code_creation.html", context)

    # Render with a dummy instance
    ccf = CourseCodeForm()
    cc = Course_Code()
    formset = CourseCodeInlineFormSet(instance=cc)
    context = {"formset" : formset, "ccf": ccf, "created": created}
    return render(request, "course_code_creation.html", context)
