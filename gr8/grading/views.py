from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from grading.models import *

def view_home(request):
    return render(request, "index.html")

# View that lists all courses.
def course_list(request):
    context = {
        'courses': Course.objects.all()
    }
    return render(request, "course_list.html", context)

def course_info(request, course_id=0):
    c = get_object_or_404(Course, pk=course_id)
    context = {
        'course': c
    }
    return render(request, "course_info.html", context)