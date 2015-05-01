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


