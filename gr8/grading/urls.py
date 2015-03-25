from django.conf.urls import patterns, include, url
from grading.views import *

#urls from grading
urlpatterns = patterns('',
    url(r'^$', view_home, name="home"),
    url(r'^course/list$', course_list, name="list"),
    url(r'^course/list/current$', course_list_current, name="current"),
    url(r'^course/(?P<course_id>\d+)$', course_info, name="info"), #Single course info page
    url(r'^course/my-courses$', courses_mine, name="courses_mine"),
    url(r'^course/cart$', shopping_bag, name="cart"),
)