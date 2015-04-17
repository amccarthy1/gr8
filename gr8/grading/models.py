from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from oauth2client.django_orm import FlowField
from oauth2client.django_orm import CredentialsField
import pickle
import base64

class CredentialsModel(models.Model):
    id = models.ForeignKey(User, primary_key=True)
    credential = CredentialsField()

    def __str__(self):
        return "Credentials for " + str(self.id)

class Department(models.Model):
    name = models.CharField('name', max_length=40, unique=True)

    def __str__(self):
        return self.name

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
            True if the enrollment was successful.
            False if the enrollment was not successful.
        """
        enrollment, created = Enrolled_In.objects.get_or_create(
            student=self,
            course=course
        )
        enrollment.is_enrolled = True
        enrollment.save()
        if (course.get_enrollment() < course.capacity):
            return True
        else:
            if created:
                enrollment.delete()
            else:
                enrollment.is_enrolled = False
                enrollment.save()
            return False

    def get_current_enrolled(self):
        """
        Returns all current Enrolled_Ins for this profile.
        """
        now = timezone.now()
        enrolled_ins = self.enrolled_in_set.filter(is_enrolled=True,
            course__term__start_date__lt=now,
            course__term__end_date__gt=now)
        return enrolled_ins

class Affiliation(models.Model):
    profile = models.ForeignKey(Profile)
    department = models.ForeignKey(Department)

    def __str__(self):
        return "%s is a part of the %r department" % (self.profile.user.username, self.department.name)

class Course_Code(models.Model):
    name = models.CharField('name', max_length=80)
    code = models.CharField('code', max_length=10, unique=True, )

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
    # TODO add comparator
    season = models.CharField('season', max_length=10, choices=TERM_CHOICES)
    year = models.IntegerField('year')
    start_date = models.DateTimeField('start date', default=timezone.now)
    end_date = models.DateTimeField('end date', default=timezone.now)

    def __str__(self):
        #human-ify the season
        season = self.season;#use the non human form as default
        #iterate through choices to find a more readable name
        for choice in self.TERM_CHOICES:
            if self.season == choice[0]:
                season = choice[1]
        return "%s, %s" % (season, self.year)


class Course(models.Model):
    course_code = models.ForeignKey(Course_Code)
    professor = models.ForeignKey(Profile, null=True, blank=True)
    term = models.ForeignKey(Term)
    section = models.IntegerField('section', null=False)
    capacity = models.IntegerField('capacity', null=False, default=40)
    credits = models.IntegerField('credits')

    def __str__(self):
        return self.name()

    def enroll_student(self, student):
        """
        NOTE: Only use this method to force-enroll a student, ignoring the
        capacity of the course. This method should only be accessible to
        course professors and sysadmins.
        Parameters:
            student: The student to enroll in this course
        Returns:
            The Enrolled_In object that was created or modified.
        """
        ei, created = Enrolled_In.objects.get_or_create(student=student, course=self)
        ei.is_enrolled = True
        ei.save()
        return ei

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


class Enrolled_In(models.Model):
    course = models.ForeignKey(Course)
    student = models.ForeignKey(Profile)
    grade = models.FloatField('grade', blank=True, null=True)
    is_enrolled = models.BooleanField("enrolled?", default=False)

    def __str__(self):
        return "%s -> '%s'" % (self.student, self.course)

    class Meta:
        verbose_name = "enrolled in"

class Prereq(models.Model):
    prereq_class = models.ForeignKey(Course_Code, related_name='prereq_set')
    course = models.ForeignKey(Course_Code, related_name='_')

    def __str__(self):
        return str(self.course)


class Room(models.Model):
    name = models.CharField('name', max_length=12, unique=True)

    def __str__(self):
        return self.name


class Course_Session(models.Model):
    #Days of the week definitions
    SUNDAY = "SUN"
    MONDAY = "MON"
    TUESDAY = "TUES"
    WEDNESDAY = "WED"
    THURSDAY = "THURS"
    FRIDAY = "FRI"
    SATURDAY = "SAT"
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
