from django.conf.urls import patterns, include, url
from grading.views import *

#urls from grading
urlpatterns = patterns('',
    url(r'^course/list$', course_list, name="list"),
    url(r'^course/(?P<course_id>\d+)$', course_info, name="info"), #Single course info page
)