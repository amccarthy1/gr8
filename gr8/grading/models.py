from  django.core.validators import MinValueValidator,MaxValueValidator
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from gr8.settings import GRADE_SCALE, GRADE_PASSING
from oauth2client.django_orm import CredentialsField
from oauth2client.django_orm import FlowField
import base64
import pickle


class CredentialsModel(models.Model):
    id = models.ForeignKey(User, primary_key=True)
    credential = CredentialsField()

    def __str__(self):
        return "Credentials for " + str(self.id)

class Profile(models.Model):
    user = models.OneToOneField(User)
    can_enroll = models.BooleanField("can enroll?", default=False)

    def __str__(self):
        return self.user.username

    def enroll_in(self, course):
        """
        Enrolls the student in the course. This method ensures that the
        course's capacity is not overflowed. Overfilled classes should still
        be allowed, but only through a professor's discretion, and that
        functionality should not be available through this method.
        Parameters:
            course: The course the student wants to enroll in
        Returns:
            Empty string if the enrollment was successful
            An error message if the enrollment was unsuccessful
        """
        if (self.can_enroll):

             # Determine if the user meets the prerequisites for the course
            if (not self.meets_prerequisites(course)):
                return "You do not meet the prerequisites for that course"

            enrollment, created = Enrolled_In.objects.get_or_create(
                student=self,
                course=course
            )
            enrollment.is_enrolled = True
            enrollment.save()

            if (course.get_enrollment() <= course.capacity):
                return ""
            else:
                if created:
                    enrollment.delete()
                else:
                    enrollment.is_enrolled = False
                    enrollment.save()
                return "This course is full, enrollment unsuccessful"

    def get_current_enrolled(self):
        """
        Returns all current Enrolled_Ins for this profile.
        """
        now = timezone.now()
        enrolled_ins = self.enrolled_in_set.filter(is_enrolled=True,
            course__term__start_date__lt=now,
            course__term__end_date__gt=now)
        return enrolled_ins

    def get_enrolled_ins(self):
        enrolled_ins = self.enrolled_in_set.filter(is_enrolled=True)
        return enrolled_ins

    def get_enrolled_by_term(self, term):
        """
        Returns all courses the student was enrolled in during the given term.
        """
        enrolled_ins = self.get_enrolled_ins().filter(course__term=term)
        return enrolled_ins

    def get_terms_attended(self):
        """
        Returns all the terms this student has been enrolled during.
        """
        #get enrolled_ins
        enrolled_ins = self.get_enrolled_ins()
        #get the courses from that set
        courses = Course.objects.filter(id__in=enrolled_ins.values('course_id'))
        #return the terms those courses are in
        return Term.objects.filter(id__in=courses.values('term_id'))

    def get_terms_up_to(self, term):
        """
        Return a collection of terms this student has been enrolled in up to
        and including the given term.
        """
        return self.get_terms_attended().filter(start_date__lte=term.start_date)


    def get_term_stats(self, term):
        """
        Return a dictionary of various stats where all key/value pairs are
        strings so that they are print-friendly.
        """
        stats = list()
        attempted = 0
        earned = 0
        grade_points = 0.0
        grade_credits = 0
        num_grades = 0
        for term in self.get_terms_up_to(term):
            for enrolled_in in self.get_enrolled_by_term(term):
                attempted += enrolled_in.course.course_code.credits
                if enrolled_in.grade is not None:
                    grade_points += enrolled_in.grade * enrolled_in.course.course_code.credits
                    grade_credits += enrolled_in.course.course_code.credits
                    #if the student passed, give them their earned credits
                    if enrolled_in.is_passing_grade():
                        earned += enrolled_in.course.course_code.credits

        #calculate the gpa
        if grade_credits == 0:
            gpa = 0
        else:
            gpa = float(grade_points) / grade_credits

        #add stats to dictionary
        stats.append(('Credits Attempted:', str(attempted)))
        stats.append(('Credits Earned:', str(earned)))
        stats.append(('GPA:', "%.2f/%.2f" % (gpa, GRADE_SCALE)))
        return stats

    def passed_class(self, code):
        try:
            ei = Enrolled_In.objects.get(student=self, course__course_code=code);
            return ei.is_passing_grade()
        except:
            return False

    def meets_prerequisites(self, code):
        if isinstance(code, Course): # allow passing in a course or code
            code = code.course_code

        prereqs = code.prereq_set.all()
        for prereq in prereqs:
            required = prereq.course
            if not self.passed_class(required):
                return False

        return True

    def is_proff(self):
        teaching_list = Course.objects.filter(professor = self)
        return len(teaching_list) > 0

class Course_Code(models.Model):
    name = models.CharField('name', max_length=80)
    code = models.CharField('code', max_length=10, unique=True, )
    credits = models.IntegerField('credits', validators=[MinValueValidator(0)])

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = "course code"

class Term(models.Model):
    #Term Choice Definitions
    FALL = "FL"
    SPRING = "SP"
    WINTER = "WT"
    SUMMER = "SM"
    TERM_CHOICES = (
        (FALL, 'Fall'),
        (SPRING, 'Spring'),
        #some less common ones
        (WINTER, 'Winter'),
        (SUMMER, 'Summer'),
    )
    season = models.CharField('season', max_length=10, choices=TERM_CHOICES)
    year = models.IntegerField('year')
    start_date = models.DateTimeField('start date', default=timezone.now)
    end_date = models.DateTimeField('end date', default=timezone.now)

    def __lt__(self, term):
        return (self.start_date < term.start_date)

    def __str__(self):
        #human-ify the season
        season = self.season;#use the non human form as default
        #iterate through choices to find a more readable name
        for choice in self.TERM_CHOICES:
            if self.season == choice[0]:
                season = choice[1]
        return "%s, %s" % (season, self.year)

    # returns a readable form of the start date
    def start(self):
        return self.start_date.strftime("%B %d, %Y")

    def end(self):
        return self.end_date.strftime("%B %d, %Y")

    # returns the currently active term object.
    def get_current_term():
        now = timezone.now()
        try:
            return Term.objects.get(start_date__lt=now, end_date__gt=now)
        except:
            return None

class Course(models.Model):
    course_code = models.ForeignKey(Course_Code)
    professor = models.ForeignKey(Profile, null=True, blank=True)
    term = models.ForeignKey(Term)
    section = models.IntegerField('section', null=False)
    capacity = models.IntegerField('capacity', null=False, default=40, validators=[MinValueValidator(0)])

    def __str__(self):
        return self.name()

    def name(self):
        return self.course_code.name

    def is_open(self):
        return self.get_enrollment() < self.capacity

    def get_enrollment(self):
        return self.enrolled_in_set.filter(is_enrolled=True).count()

    def get_prof(self):

        if self.professor is None:
            return "Staff"
        else:
            return self.professor.user.first_name + " " + self.professor.user.last_name

    def desc_string(self):
        return "[%s S%d]: %s" % (str(self.course_code), self.section,
            self.course_code.name)

    def get_current_courses():
        now = timezone.now()
        return Course.objects.filter(term__start_date__lt=now, term__end_date__gt=now)

    def get_sessions(self):
        return Course_Session.objects.filter(course=self)

    def get_course_times(self):

        # a dictionary with keys of start time concatenated with end time with a list of days in abbreviated form
        times = {}

        sessions = self.get_sessions()

        for session in sessions:

            # if the start and end time is already in the dictionary, add the day to the correct spot in the keys list
            if (session.start_time.strftime("%I:%M %p")) + " - " + (session.end_time.strftime("%I:%M %p")) in times:
                times[(session.start_time.strftime("%I:%M %p")) + " - " + (session.end_time.strftime("%I:%M %p"))][session.day_to_int()] = session.get_abbrev()

            # else create the time and end time in the dictionary
            else:
                times[(session.start_time.strftime("%I:%M %p")) + " - " + (session.end_time.strftime("%I:%M %p"))] = ["","","","","","",""]
                times[(session.start_time.strftime("%I:%M %p")) + " - " + (session.end_time.strftime("%I:%M %p"))][session.day_to_int()] = session.get_abbrev()

        timesStr = ""
        counter = 0

        # loop over all start and end time keys
        for time in times:

            # for the day abbreviation in the keys list, append it to a string
            for day in times[time]:
                timesStr += day

            timesStr += " " + str(time)
            if counter < len(times) -1:
                timesStr += "<br/>"

            counter +=1

        return timesStr

    def get_prereqs(self):
        return Prereq.objects.filter(prereq_course = self.course_code)

    def credits(self):
         return self.course_code.credits

class Enrolled_In(models.Model):
    course = models.ForeignKey(Course)
    student = models.ForeignKey(Profile)
    grade = models.FloatField('grade', blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(GRADE_SCALE)])
    is_enrolled = models.BooleanField("enrolled?", default=False)

    def __str__(self):
        return "%s -> '%s'" % (self.student, self.course)

    class Meta:
        verbose_name = "enrolled in"

    def is_passing_grade(self):
        # If we want grading to be more modular or we need to change the
        # passing threshold, it should be done here
        return self.grade >= GRADE_PASSING

class Prereq(models.Model):
    prereq_course = models.ForeignKey(Course_Code, related_name='prereq_set')
    course = models.ForeignKey(Course_Code, related_name='_' , verbose_name='Optional Prereq')

    def __str__(self):
        return str(self.course)


class Room(models.Model):
    name = models.CharField('name', max_length=12, unique=True)

    def __str__(self):
        return self.name


class Course_Session(models.Model):
    #Days of the week definitions
    SUNDAY = "U"
    MONDAY = "M"
    TUESDAY = "T"
    WEDNESDAY = "W"
    THURSDAY = "R"
    FRIDAY = "F"
    SATURDAY = "S"
    DAYS_OF_WEEK_CHOICES = (
        (SUNDAY, 'Sunday'),
        (MONDAY, 'Monday'),
        (TUESDAY, 'Tuesday'),
        (WEDNESDAY, 'Wednesday'),
        (THURSDAY, 'Thursday'),
        (FRIDAY, 'Friday'),
        (SATURDAY, 'Saturday')
    )

    course = models.ForeignKey(Course)
    room = models.ForeignKey(Room)
    start_time = models.TimeField('start time')
    end_time = models.TimeField('end time')
    day = models.CharField('day of week', max_length=5, choices=DAYS_OF_WEEK_CHOICES)

    def __str__(self):
        return "%s: (%s) %s-%s, %s" % (self.course, self.room,
            self.start_time, self.end_time, self.day)

    class Meta:
        verbose_name = "course session"

    def day_to_int(self):
        """
        Returns the integer form of the day where SUNDAY is 0 and the other Days
        increment by 1 for each day pas sunday.
        """
        for i in range(0,len(self.DAYS_OF_WEEK_CHOICES)):
            choice = self.DAYS_OF_WEEK_CHOICES[i][0]
            if self.day == choice:
                return i

    def get_abbrev(self):
        return self.DAYS_OF_WEEK_CHOICES[self.day_to_int()][0]

    # static method to look up the shortened day string.
    def lookup_day(day):
        for tup in Course_Session.DAYS_OF_WEEK_CHOICES:
            if day.lower() == tup[1].lower():
                return tup[0]
        return None # and play the price is right losing horn.

