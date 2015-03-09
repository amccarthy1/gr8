from django.shortcuts import render
from django.http import HttpResponse
from grading.models import *

# View that lists all courses.
def courses_list(request):
    context = {
        'courses': Course.objects.all()
    }
    return render(request, "course_list.html", context)