from django.db import models
from django.contrib.auth.models import User

TERMS = (
    ('Fall', 'Fall'),
    ('Spring', 'Spring'),
    #some less common ones
    ('Winter', 'Winter'),
    ('Summer', 'Summer'),
)

DAYS_OF_WEEK = (
    ('Sunday', 'Sunday'),
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
    ('Saturday', 'Saturday')
)


class Department(models.Model):
    name = models.CharField(max_length=40, null=False, blank=False)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User)
    department = models.ForeignKey(Department)
    can_enroll = models.BooleanField(default=False)

    def __str__(self):
        return "Profile for user %r" % self.user.username


class Course_Code(models.Model):
    code = models.CharField(max_length=10, null=False, blank=False)

    def __str__(self):
        return self.code


class Term(models.Model):
    # TODO add comparator
    season = models.CharField(max_length=10, choices=TERMS)
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
    course = models.ForeignKey(Course)
    room = models.ForeignKey(Room)
    start_time = models.TimeField()
    end_time = models.TimeField()
    day = models.CharField(max_length=1, choices=DAYS_OF_WEEK)

    def __str__(self):
        return "%s: (%s) %s-%s, %s" % (self.course, self.room,
            self.start_time, self.end_time, self.day)