from django.conf.urls import patterns, include, url
from django.core import serializers
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from grading.forms import CourseForm
from grading.models import *

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
		return JsonResponse({"success": False, "caller-error": "ajax/submit_course requries POST"})
	course_code = get_object_or_404(Course_Code, code=request.POST["code"])
	cf = CourseForm(request.POST)
	if cf.is_valid():
		course = cf.save(commit=False)
		course.course_code = course_code
		course.save()
		response["course_name"] = course.course_code.name
	response["success"] = True
	return JsonResponse(response)



urlpatterns = patterns('',
	url(r'^lookup_code$', lookup_code),
	url(r'^validate_course$', validate_course),
	url(r'^submit_course$', submit_course),
)