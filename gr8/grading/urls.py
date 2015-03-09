from django.conf.urls import patterns, include, url
from grading.views import *

#urls from grading
urlpatterns = patterns('',
    url(r'^courses/list/$', courses_list),
)