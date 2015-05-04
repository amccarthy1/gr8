from django.test import TestCase
from django.db.utils import IntegrityError
from grading.models import *
from django.utils import timezone
from datetime import timedelta

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

        NCoriale = User.objects.create(username = "NCoriale", first_name = "Nick", last_name = "Coriale", password = "nickiscool")
        Profile.objects.create(user = NCoriale, can_enroll = True)

        AMcCarthy = User.objects.create(username = "AMcCarthy", first_name = "Adam", last_name = "McCarthy", password = "admaniskindacool")
        Profile.objects.create(user = AMcCarthy, can_enroll = False)

        test_term_past = Term.objects.create(season = "Spring",year = 2013)
        test_term = Term.objects.create(season = "Spring",year = 2015, start_date = timezone.now() , end_date = timezone.now() + timedelta(days=1) )
        test_term_future = Term.objects.create(season = "Spring",year = 2020)

        c_code = Course_Code.objects.create(name="Intro To Software Engineering", code="261", credits=4)
        Course.objects.create(course_code = c_code, professor = krutz, term = test_term , section = 1 , capacity = 40 )

        c_code_2 = Course_Code.objects.create(name="Software Process", code="256", credits=4)
        Course.objects.create(course_code = c_code_2, professor = krutz, term = test_term , section = 1 , capacity = 35 )

        c_code_3 = Course_Code.objects.create(name="Software Magic", code="999", credits=4)
        Course.objects.create(course_code = c_code_3, professor = krutz, term = test_term_future , section = 1 , capacity = 35 )

        c_code_4 = Course_Code.objects.create(name="Software Magic", code="777", credits=4)
        Course.objects.create(course_code = c_code_4, professor = krutz, term = test_term_past , section = 1 , capacity = 35 )

    def test_enroll_in(self):
        c_code = Course_Code.objects.get(code="261")
        test_course = Course.objects.get(course_code = c_code)
        krutz = Profile.objects.get(user__username = "DKrutz")
        MWashburn = Profile.objects.get(user__username = "MWashburn")

        self.assertEqual(0, test_course.enrolled_in_set.filter(is_enrolled=True).count())
        MWashburn.enroll_in(test_course)
        self.assertEqual(1, test_course.enrolled_in_set.filter(is_enrolled=True).count())

        enrolled_in = Enrolled_In.objects.get(student = MWashburn, course = test_course)

        self.assertEqual(test_course, enrolled_in.course)

    def test_enroll_in_on_profile_that_cannot_enroll(self):

        c_code = Course_Code.objects.get(code="261")
        test_course = Course.objects.get(course_code = c_code)
        krutz = Profile.objects.get(user__username = "DKrutz")
        AMcCarthy = Profile.objects.get(user__username = "AMcCarthy")

        self.assertEqual(0, test_course.enrolled_in_set.filter(is_enrolled=True).count())
        AMcCarthy.enroll_in(test_course)
        self.assertEqual(0, test_course.enrolled_in_set.filter(is_enrolled=True).count())

        enrolled_in = Enrolled_In.objects.filter(student = AMcCarthy, course = test_course)

        self.assertEqual(0, len(enrolled_in))

    def test_enroll_in_full_class(self):
        test_term = Term.objects.get(season = "Spring",year = 2015)

        krutz = Profile.objects.get(user__username = "DKrutz")
        MWashburn = Profile.objects.get(user__username = "MWashburn")

        c_code = Course_Code.objects.get(name="Software Process", code="256", credits=4)
        test_course = Course.objects.create(course_code = c_code, professor = krutz, term = test_term , section = 2 , capacity = 0 )

        self.assertEqual(0, test_course.enrolled_in_set.filter(is_enrolled=True).count())
        MWashburn.enroll_in(test_course)
        self.assertEqual(0, test_course.enrolled_in_set.filter(is_enrolled=True).count())

        enrolled_ins = test_course.enrolled_in_set.filter(student = MWashburn, course = test_course)

        self.assertEqual(0, len(enrolled_ins))

    def test_get_current_enrolled(self):

        MWashburn = Profile.objects.get(user__username = "MWashburn")

        enrolled_ins = MWashburn.get_current_enrolled();

        self.assertEqual(0, len(enrolled_ins))

        c_code = Course_Code.objects.get(code="261")
        test_course = Course.objects.get(course_code = c_code)

        MWashburn.enroll_in(test_course)

        enrolled_ins = MWashburn.get_current_enrolled();

        self.assertEqual(1, len(enrolled_ins))

        c_code = Course_Code.objects.get(code="256")
        test_course = Course.objects.get(course_code = c_code)

        MWashburn.enroll_in(test_course)

        enrolled_ins = MWashburn.get_current_enrolled();

        self.assertEqual(2, len(enrolled_ins))

        c_code = Course_Code.objects.get(code="999")
        test_course = Course.objects.get(course_code = c_code)

        MWashburn.enroll_in(test_course)

        enrolled_ins = MWashburn.get_current_enrolled();

        self.assertEqual(2, len(enrolled_ins))

        c_code = Course_Code.objects.get(code="777")
        test_course = Course.objects.get(course_code = c_code)

        MWashburn.enroll_in(test_course)

        enrolled_ins = MWashburn.get_current_enrolled();

        self.assertEqual(2, len(enrolled_ins))

        enrolled_ins = Enrolled_In.objects.filter(student = MWashburn)

        self.assertEqual(4, len(enrolled_ins))

    def test_get_enrolled_ins(self):

        MWashburn = Profile.objects.get(user__username = "MWashburn")

        c_code = Course_Code.objects.get(code="261")
        test_course = Course.objects.get(course_code = c_code)

        MWashburn.enroll_in(test_course)

        c_code = Course_Code.objects.get(code="256")
        test_course = Course.objects.get(course_code = c_code)

        MWashburn.enroll_in(test_course)

        c_code = Course_Code.objects.get(code="999")
        test_course = Course.objects.get(course_code = c_code)

        MWashburn.enroll_in(test_course)

        c_code = Course_Code.objects.get(code="777")
        test_course = Course.objects.get(course_code = c_code)

        MWashburn.enroll_in(test_course)

        enrolled_ins = MWashburn.get_enrolled_ins()

        self.assertEqual(4, len(enrolled_ins))

    def test_get_enrolled_by_term(self):

        MWashburn = Profile.objects.get(user__username = "MWashburn")

        c_code = Course_Code.objects.get(code="261")
        test_course = Course.objects.get(course_code = c_code)

        MWashburn.enroll_in(test_course)

        c_code = Course_Code.objects.get(code="256")
        test_course = Course.objects.get(course_code = c_code)

        MWashburn.enroll_in(test_course)

        c_code = Course_Code.objects.get(code="999")
        test_course = Course.objects.get(course_code = c_code)

        MWashburn.enroll_in(test_course)

        c_code = Course_Code.objects.get(code="777")
        test_course = Course.objects.get(course_code = c_code)

        MWashburn.enroll_in(test_course)

        test_term_past = Term.objects.get(season = "Spring",year = 2013)
        test_term = Term.objects.get(season = "Spring",year = 2015)
        test_term_future = Term.objects.get(season = "Spring",year = 2020)

        enrolled_ins = MWashburn.get_enrolled_by_term(test_term_past)
        self.assertEqual(1, len(enrolled_ins))

        enrolled_ins = MWashburn.get_enrolled_by_term(test_term)
        self.assertEqual(2, len(enrolled_ins))

        enrolled_ins = MWashburn.get_enrolled_by_term(test_term_future)
        self.assertEqual(1, len(enrolled_ins))

    def test_get_terms_attended(self):

        NCoriale = Profile.objects.get(user__username = "NCoriale")

        c_code = Course_Code.objects.get(code="777")
        test_course = Course.objects.get(course_code = c_code)

        NCoriale.enroll_in(test_course)

        test_term_past = Term.objects.get(season = "Spring",year = 2013)

        self.assertEqual(1, (len(NCoriale.get_terms_attended())))

        self.assertTrue(test_term_past in NCoriale.get_terms_attended())