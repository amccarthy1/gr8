from django.conf.urls import patterns, include, url
from django.contrib import admin
from grading.views import login, logout, auth_return, googleLogin
from grading.adminViews import *
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
    url(r'^oauth2callback/', auth_return, name="auth_return"),
    url(r'^googleLogin/$', googleLogin, name="google_login"),
)
