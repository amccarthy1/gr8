from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.utils import timezone
from grading.models import *
import datetime
from django.utils import timezone
from gr8 import settings
import os
import logging
import httplib2
from apiclient.discovery import build
from oauth2client import xsrfutil
from oauth2client.client import flow_from_clientsecrets, AccessTokenRefreshError
from oauth2client.django_orm import Storage

# CLIENT_SECRETS, name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret, which are found
# on the API Access tab on the Google APIs
# Console <http://code.google.com/apis/console>
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), '..', 'client_secrets.json')

FLOW = flow_from_clientsecrets(
    CLIENT_SECRETS,
    scope='https://www.googleapis.com/auth/calendar',
    redirect_uri='http://localhost:8000/oauth2callback')

def view_home(request):
    return render(request, "index.html")

def login(request):

    if request.user.is_authenticated():
        return redirect("grading:home")

    if request.method == "POST":
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            if Profile.objects.filter(user=user).count() == 0:
                Profile.objects.create(user=user)
            return redirect(request.POST.get('next','grading:home'))
        else:
            return render(request, "login.html", {"login_failed": True})

    return render(request, "login.html")

def logout(request):

    if request.user.is_authenticated():
        auth.logout(request)
        return render(request, "index.html")
    else:
        return redirect("grading:home")


# View that lists all courses.
@login_required
def course_list(request):
    context = {
        'courses': Course.objects.all(),
        'header': "All Courses"
    }
    return render(request, "course_list.html", context)

@login_required
def course_list_current(request):
    context = {
        'courses': Course.get_current_courses(),
        'header': "Current Courses"
    }
    return render(request, "course_list.html", context)

@login_required
def course_info(request, course_id=0):
    c = get_object_or_404(Course, pk=course_id)
    profile = request.user.profile

    can_enroll = (profile is not None and profile.can_enroll and c.professor != profile)
    is_professor = (c.professor == profile)

    is_enrolled = False
    is_in_cart = False
    success = True
    if profile:
        #is_enrolled is true if there is a Enrolled_In w/ this student & course
        is_enrolled = len(Enrolled_In.objects.filter(course=c ,student=profile, is_enrolled=True)) > 0
        is_in_cart = len(Enrolled_In.objects.filter(course=c, student=profile, is_enrolled=False)) > 0
        #when user tries to enroll or add to bucket
        if can_enroll and request.method == "POST":
            if "enroll" in request.POST:
                success = profile.enroll_in(c)
                is_enrolled = success
            elif not is_enrolled and not is_in_cart and "cart" in request.POST:
                enrolled_in = Enrolled_In.objects.create(course=c, student=profile, is_enrolled=False)
                is_in_cart = True
            elif not is_enrolled and is_in_cart and "cart_remove" in request.POST:
                enrolled_in = Enrolled_In.objects.filter(course=c, student=profile, is_enrolled=False)
                enrolled_in.delete()
                is_in_cart = False
            elif is_enrolled and "drop" in request.POST:
                enrolled_in = Enrolled_In.objects.filter(course=c, student=profile, is_enrolled=True)
                enrolled_in.delete()
                is_enrolled = False

    context = {
        'course': c,
        'can_enroll' : can_enroll,
        'is_enrolled' : is_enrolled,
        'is_in_cart' : is_in_cart,
        'enroll_success' : success,
        'is_professor' : is_professor,
    }
    return render(request, "course_info.html", context)

@login_required
def courses_mine(request):
    profile = request.user.profile
    if profile is None:
        raise Http404()

    #get only current courses that the user is in
    enrolled_ins = profile.get_current_enrolled()

    #get current courses the user is the professor of
    professor_of = Course.get_current_courses().filter(professor=profile)

    context = {
        'request': request,
        'enrolled_ins' : enrolled_ins,
        'professor_of' : professor_of,
    }

    return render(request, "courses_mine.html", context)

@login_required
def shopping_bag(request):
    profile = request.user.profile
    if profile is None:
        raise Http404()

    if request.method == "POST":
        if "check_conflicts" in request.POST:
            profile = request.user.profile
            if profile is None:
                raise Http404()
            storage = Storage(CredentialsModel, 'id', request.user, 'credential')
            credential = storage.get()
            # if the user is not authenticated with google, authenticate
            if credential is None or credential.invalid == True:
                FLOW.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY,
                                                           request.user)
                authorize_url = FLOW.step1_get_authorize_url()
                return HttpResponseRedirect(authorize_url)

            else:

                # user is authenticated with google at this point

                # get my current shopping cartcourses
                my_cart_courses = profile.enrolled_in_set.filter(is_enrolled=False)

                # get calendar events
                http = httplib2.Http()
                http = credential.authorize(http)
                service = build("calendar", "v3", http=http)

                now_start_time = str(datetime.datetime.now().isoformat('T')) + "-05:00"
                events = service.events().list(calendarId='primary', timeMin=now_start_time).execute()

                # day of the week -> list of events
                recurring_events_dict = {}

                # course session -> calendar event
                conflict_dict = {}

                recurring_events = events.get('items', [])

                
                for item in events.get('items', []):
                    # check if event is a recurring event
                    if 'recurrence' in item:
                        r_event = item
                        recur_string = r_event['recurrence'][0]

                        # recur_string looks like "'RRULE:FREQ=WEEKLY;UNTIL=20150515T140000Z;BYDAY=FR"
                        day_string = ""
                        start_index = recur_string.find('DAY=')
                        # the day string is always 2 characters i.e. "FR", or "WE"
                        day_string = recur_string[start_index + 4:start_index + 6 ]

                        # add event to day key in dictionary
                        if day_string in recurring_events_dict:
                            recurring_events_dict[day_string].append(r_event)
                        else:
                            recurring_events_dict[day_string] = []
                            recurring_events_dict[day_string].append(r_event)
                        
                        
                for enrolled_in in my_cart_courses:
                    sessions = enrolled_in.course.course_session_set.all()
                    for session in sessions:
                        day = session.day
                        # i.e. convert 'FRI' to 'FR'
                        day_formatted = day[0:2].upper()
                        if day_formatted in recurring_events_dict:
                            for recurring_event in recurring_events_dict[day_formatted]:
                                # r_start and r_end are dictionaries
                                r_start = recurring_event['start']
                                r_end = recurring_event['end']
                                r_start_timestamp = r_start['dateTime']
                                r_end_timestamp = r_end['dateTime']
                                start_index = r_start_timestamp.find('T')
                                r_start_time_formatted = datetime.datetime.strptime(r_start_timestamp[start_index + 1 : start_index + 9], "%H:%M:%S").time()
                                start_index = r_end_timestamp.find('T')
                                r_end_time_formatted = datetime.datetime.strptime(r_end_timestamp[start_index + 1 : start_index + 9], "%H:%M:%S").time()
                                if ((r_start_time_formatted >= session.start_time) and (r_start_time_formatted <= session.end_time)) or ((r_start_time_formatted >= session.start_time) and (r_end_time_formatted >= session.end_time)):
                                    conflict_dict[session] = recurring_event


                context = {
                    'profile' : profile,
                    'cart_courses' : my_cart_courses,
                    'conflict_dict' : conflict_dict,
                    'events' : recurring_events,
                }

                return render(request, "shopping_cart.html", context)
        elif "enroll_all" in request.POST:
            my_cart_courses = profile.enrolled_in_set.filter(is_enrolled=False)
            for enrolled_in in my_cart_courses:
                enrolled_in.is_enrolled = True
                enrolled_in.save()

    my_cart_courses = profile.enrolled_in_set.filter(is_enrolled=False)

    context = {
        'profile' : profile,
        'cart_courses' : my_cart_courses,
    }

    return render(request, "shopping_cart.html", context)

@login_required
def schedule(request):
    profile = request.user.profile
    if profile is None:
        raise Http404()

    enrolled_ins = profile.get_current_enrolled()

    #build list of this weeks days' dates
    weekDates = []
    today = timezone.now()
    for i in range(-1 - today.weekday(), 8 - today.weekday()):
        date = today + datetime.timedelta(days=i)
        dateString = date.strftime("%Y-%m-%d")
        weekDates.append(dateString)

    #make a list of json to be rendered as schedule items
    sessions = []
    for enrolled_in in enrolled_ins:
        #get all sessions for this course
        course_sessions = enrolled_in.course.get_sessions()

        #jsonify all course sessions
        for course_session in course_sessions:
            #grab the string of the title, startTime, and endTime
            title = str(course_session.course)
            description = str(course_session.course.get_prof()) + "<br/>" + str(course_session.room)

            url = reverse('grading:info', args=(course_session.course.id,))
            date = weekDates[course_session.day_to_int()]
            #T seperates date from time for fullcalendar's format
            start = date + 'T' + course_session.start_time.strftime("%H:%M:%S")
            end = date + 'T' + course_session.end_time.strftime("%H:%M:%S")

            #format the json with date, start, end
            #date should be of format YYYY-MM-DDTHH:MM:SS
            session = "{ title: '%s', start: '%s', end: '%s', description: '%s', url: '%s'}" % (title, start, end, description, url)
            sessions.append(session)

    return render(request, "my_schedule.html", {'sessions' : sessions})

def googleLogin(request):
    storage = Storage(CredentialsModel, 'id', request.user, 'credential')
    credential = storage.get()
    if credential is None or credential.invalid == True:
        FLOW.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY,
                                                   request.user)
        authorize_url = FLOW.step1_get_authorize_url()
        return HttpResponseRedirect(authorize_url)

    else:
        http = httplib2.Http()
        http = credential.authorize(http)
        service = build("calendar", "v3", http=http)

        test_time = str(datetime.datetime.now().isoformat('T')) + "-05:00"
        events = service.events().list(calendarId='primary', timeMin=test_time).execute()

        return render(request, "index.html", {})


@login_required
def auth_return(request):
    if not xsrfutil.validate_token(settings.SECRET_KEY, request.REQUEST['state'], 
        request.user):
        return  HttpResponseBadRequest()
    credential = FLOW.step2_exchange(request.REQUEST)
    storage = Storage(CredentialsModel, 'id', request.user, 'credential')
    storage.put(credential)
    return HttpResponseRedirect("/")
