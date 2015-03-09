from django.conf.urls import patterns, include, url
from django.contrib import admin

# Import URLs from grading app
from grading.urls import urlpatterns as grading_urls

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'gr8.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^', include(grading_urls, namespace="grading")),
    url(r'^admin/', include(admin.site.urls)),
)
