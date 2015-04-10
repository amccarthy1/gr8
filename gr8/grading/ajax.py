from django.conf.urls import patterns, include, url
from django.core import serializers
from django.http import JsonResponse
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

urlpatterns = patterns('',
	url(r'^lookup_code$', lookup_code),
)