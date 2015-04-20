from django.conf.urls import patterns, include, url
from grading.views import *
from grading.pdf import render_transcript
from grading.ajax import urlpatterns as ajax_urls
from grading.adminViews import *

#urls from grading
urlpatterns = patterns('',
    url(r'^$', view_home, name="home"),
    url(r'^course/list$', course_list, name="list"),
    url(r'^course/list/current$', course_list_current, name="current"),
    url(r'^course/(?P<course_id>\d+)$', course_info, name="info"), #Single course info page
    url(r'^course/my-courses$', courses_mine, name="courses_mine"),
    url(r'^course/cart$', shopping_bag, name="cart"),
    url(r'^pdf$', render_transcript, name="pdf"), #TODO Move this URL to somewhere more useful.
    url(r'^my-schedule', schedule, name="my-schedule"),

    #admin urls
    url(r'^register$', user_registration, name="register"),
    url(r'^rooms$', room_creation, name="room_creation"),
    url(r'^course/create$', create_course, name="course_creation"),
    url(r'^terms$',term_creation, name="term_creation"),
    url(r'^course/code/create$', create_course_code, name="create_course_code"),
    url(r'^course/grade/(?P<course_id>\d+)/(?P<profile_id>\d+)$', course_grade, name="course_grade"),

    url(r'^ajax/', include(ajax_urls, namespace="ajax")), # Ajax functions defined in ajax.py
    url(r'^grades$', my_grades, name="my_grades"),

)