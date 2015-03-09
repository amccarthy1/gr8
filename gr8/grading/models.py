from django.db import models
from django.contrib.auth.models import User

class Department(models.Model):
    name = models.CharField(max_length=40, null=False, blank=False)

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User)
    can_enroll = models.BooleanField(default=False)

    def __str__(self):
        return "Profile for user %r" % self.user.username

class Affiliation(models.Model):
    profile = models.ForeignKey(Profile)
    department = models.ForeignKey(Department)

    def __str__(self):
        return "%s is a part of the %r department" % (self.profile.user.username, self.department.name)

class Course_Code(models.Model):
    code = models.CharField(max_length=10, null=False, blank=False)

    def __str__(self):
        return self.code


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
    season = models.CharField(max_length=10, choices=TERM_CHOICES)
    year = models.IntegerField()

    def __str__(self):
        return "%s %s" % (self.season, self.year)


class Course(models.Model):
    name = models.CharField(max_length=80, null=False, blank=False)
    section = models.IntegerField(null=False)
    course_code = models.ForeignKey(Course_Code)
    professor = models.ForeignKey(Profile, null=True)
    term = models.ForeignKey(Term)

    def __str__(self):
        return self.name


class Enrolled_In(models.Model):
    course = models.ForeignKey(Course)
    student = models.ForeignKey(Profile)
    grade = models.FloatField()

    def __str__(self):
        return "%s: Enrolled in %s" % (self.student, self.course)


class Prereq(models.Model):
    prereq_class = models.ForeignKey(Course, related_name='prereq')
    course = models.ForeignKey(Course, related_name='_')

    def __str__(self):
        return str(self.course)


class Room(models.Model):
    name = models.CharField(max_length=12, null=False, blank=False)

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
    start_time = models.TimeField()
    end_time = models.TimeField()
    day = models.CharField(max_length=1, choices=DAYS_OF_WEEK_CHOICES)

    def __str__(self):
        return "%s: (%s) %s-%s, %s" % (self.course, self.room,
            self.start_time, self.end_time, self.day)