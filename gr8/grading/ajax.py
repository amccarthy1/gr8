from django.conf.urls import patterns, include, url
from django.core import serializers
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from grading.forms import CourseForm
from grading.models import *
from datetime import datetime
import sys

def lookup_code(request):
    code = request.GET['code']
    json = {
        "code": code,
        "name": "",
    }
    if (code != ""):
        codes = Course_Code.objects.filter(code=code)
        if len(codes):
            json['name'] = codes[0].name

    return JsonResponse(json)

def validate_course(request):
    response = {
        "success": False,
        "errors": {
        },
    }
    if request.method != "GET":
        return JsonResponse({"success": False, "caller_error": "ajax/validate_course requires GET"})
    cf = CourseForm(request.GET)
    course_code_exists = Course_Code.objects.filter(code=request.GET['code']).count()
    if course_code_exists == 0:
        response["errors"].update({"code": "Course code not found"})
    if cf.is_valid() and course_code_exists != 0:
        response['success'] = True
    else: # some errors
        response["errors"].update(cf.errors)

    return JsonResponse(response)

def submit_course(request):
    response = {
        "success": False,
        "course_name": None
    } # We're bad programmers so we'll just assume the user doesn't know javascript
    if request.method != "POST":
        return JsonResponse({"success": False, "caller-error": "ajax/submit_course requires POST"})
    course_code = get_object_or_404(Course_Code, code=request.POST["code"])
    cf = CourseForm(request.POST)
    if cf.is_valid():
        course = cf.save(commit=False)
        course.course_code = course_code
        section = 1
        section += Course.objects.filter(course_code = course_code).count()
        course.section = section
        course.save()
        response["course_name"] = course.course_code.name
        response["course_id"] = course.id
    response["success"] = True
    return JsonResponse(response)

# validate (but do not save) a course session.
def validate_session(request):
    response = {
        "success": True,
        "errors": {},
    }
    if request.method != "GET":
        return JsonResponse({"success": False, "caller_error": "ajax/validate_session requires GET"})

    try:
        datetime.strptime(request.GET["start-time"], "%H:%M")
    except ValueError:
        response['success'] = False
        response['errors']['start-time'] = "Time must be of form 'HH:MM'"

    try:
        datetime.strptime(request.GET["end-time"], "%H:%M")
    except ValueError:
        response['success'] = False
        response['errors']['end-time'] = "Time must be of form 'HH:MM'"

    try:
        Room.objects.get(name=request.GET['room'])
    except:
        response['success'] = False
        response['errors']['room'] = "Room not found"


    return JsonResponse(response)

def submit_session(request):
    response = {
        "success": True
    }
    if request.method != "POST":
        return JsonResponse({"success": False, "caller_error": "ajax/submit_session requires POST"})

    for day in ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday" ,"Sunday"):
        # try:
        if (request.POST[day] == "true"):
            start = datetime.strptime(request.POST["start-time"], "%H:%M")
            end = datetime.strptime(request.POST["end-time"], "%H:%M")
            room = Room.objects.get(name=request.POST["room"])
            course = Course.objects.get(id=request.POST["course-id"])
            session = Course_Session.objects.create(course=course, start_time=start, end_time=end, room=room, day=Course_Session.lookup_day(day))

        # except:
            # print(sys.exc_info()[0])
            # response["success"] = False

    return JsonResponse(response)

urlpatterns = patterns('',
    url(r'^lookup_code$', lookup_code),
    url(r'^validate_course$', validate_course),
    url(r'^submit_course$', submit_course),
    url(r'^validate_session$', validate_session),
    url(r'^submit_session$', submit_session),
)