from django.test import TestCase
from django.db.utils import IntegrityError
from grading.models import *

class CourseCodeTests(TestCase):
    def setUp(self):
        Course_Code.objects.create(name="Intro To Software Engineering", code="261", credits=4)

    def test_course_code(self):
        courseCode = Course_Code.objects.get(code="261")
        self.assertEqual(courseCode.name, "Intro To Software Engineering")

    def test_course_code_unique(self):
        try:
            Course_Code.objects.create(name="Intro To Software Engineering", code="261", credits=4)
            self.fail("Course Code was not unique")
        except IntegrityError:
            pass

class RoomTests(TestCase):
    def setUp(self):
        roomStr = "GOL-1550"
        Room.objects.create(name=roomStr)

    def test_room(self):
        roomStr = "GOL-1550"
        room = Room.objects.get(name=roomStr)
        self.assertEqual(room.name, roomStr)

class ProfileTests(TestCase):
    def setUp(self):
        krutzUser =User.objects.create(username = "DKrutz", first_name = "Dan", last_name = "Krutz", password = "Daniscool")
        krutz = Profile.objects.create(user = krutzUser, can_enroll = True)

        MWashburn = User.objects.create(username = "MWashburn", first_name = "Mike", last_name = "Washburn", password = "mikeisnotcool")
        Profile.objects.create(user = MWashburn, can_enroll = True)

        test_term = Term.objects.create(season = "Spring",year = 2015)

        c_code = Course_Code.objects.create(name="Intro To Software Engineering", code="261", credits=4)
        Course.objects.create(course_code = c_code, professor = krutz, term = test_term , section = 1 , capacity = 40 )


    def test_enroll_in(self):
        c_code = Course_Code.objects.get(code="261")
        test_course = Course.objects.get(course_code = c_code)
        krutz = Profile.objects.get(user__username = "DKrutz")

        self.assertEqual(0, test_course.enrolled_in_set.filter(is_enrolled=True).count())
        krutz.enroll_in(test_course)
        self.assertEqual(1, test_course.enrolled_in_set.filter(is_enrolled=True).count())