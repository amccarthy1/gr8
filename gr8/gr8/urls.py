from django.conf.urls import patterns, include, url
from django.contrib import admin
from grading.views import login, logout
from grading.adminViews import user_registration, room_creation, create_course, term_creation
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm

# Import URLs from grading app
from grading.urls import urlpatterns as grading_urls

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'gr8.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^', include(grading_urls, namespace="grading")),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', login, name="login"),
    url(r'^logout/$', logout, name="logout"),
    url(r'^register/$', user_registration, name="register"),
    url(r'^rooms/$', room_creation, name="room_creation"),
    url(r'^terms/$',term_creation, name="term_creation"),
    url(r'^course/create/$', create_course, name="course_creation"),
)
