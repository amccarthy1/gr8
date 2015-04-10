from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Department(models.Model):
    name = models.CharField(max_length=40, null=False, blank=False)

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User)
    can_enroll = models.BooleanField(default=False)

    def __str__(self):
        return "Profile for user %r" % self.user.username

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

class Affiliation(models.Model):
    profile = models.ForeignKey(Profile)
    department = models.ForeignKey(Department)

    def __str__(self):
        return "%s is a part of the %r department" % (self.profile.user.username, self.department.name)

class Course_Code(models.Model):
    name = models.CharField(max_length=80, null=False, blank=False)
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
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=timezone.now)

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
    section = models.IntegerField(null=False)
    capacity = models.IntegerField(null=False, default=40)
    credits = models.IntegerField()

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
            return "STAFF"
        else:
            return self.professor.user.first_name + " " + self.professor.user.last_name

    def desc_string(self):
        return "[%s S%d]: %s" % (str(self.course_code), self.section,
            self.course_code.name)

    def get_current_courses():
        now = timezone.now()
        return Course.objects.filter(term__start_date__lt=now, term__end_date__gt=now)


class Enrolled_In(models.Model):
    course = models.ForeignKey(Course)
    student = models.ForeignKey(Profile)
    grade = models.FloatField(blank=True, null=True)
    is_enrolled = models.BooleanField(default=False)

    def __str__(self):
        return "%s: Enrolled in %s" % (self.student, self.course)


class Prereq(models.Model):
    prereq_class = models.ForeignKey(Course_Code, related_name='prereq_set')
    course = models.ForeignKey(Course_Code, related_name='_')

    def __str__(self):
        return str(self.course)


class Room(models.Model):
    name = models.CharField(max_length=12, null=False, blank=False, unique=True)

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
    day = models.CharField(max_length=5, choices=DAYS_OF_WEEK_CHOICES)

    def __str__(self):
        return "%s: (%s) %s-%s, %s" % (self.course, self.room,
            self.start_time, self.end_time, self.day)