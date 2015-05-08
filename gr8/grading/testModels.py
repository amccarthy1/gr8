from django.test import TestCase
from django.db.utils import IntegrityError
from grading.models import *
from django.utils import timezone
from datetime import timedelta
from gr8.settings import GRADE_SCALE, GRADE_PASSING


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


class CourseTests(TestCase):
    def setUp(self):
        krutzUser =User.objects.create(username = "DKrutz", first_name = "Dan", last_name = "Krutz", password = "Daniscool")
        krutz = Profile.objects.create(user = krutzUser, can_enroll = True)

        MWashburn = User.objects.create(username = "MWashburn", first_name = "Mike", last_name = "Washburn", password = "mikeisnotcool")
        Profile.objects.create(user = MWashburn, can_enroll = True)

        NCoriale = User.objects.create(username = "NCoriale", first_name = "Nick", last_name = "Coriae", password = "nickiscool")
        Profile.objects.create(user = NCoriale, can_enroll = True)

        test_room = Room.objects.create(name="GOL-1550")

        test_term_past = Term.objects.create(season = "Spring",year = 2013, start_date = timezone.now() - timedelta(days=365*2),  end_date = timezone.now() + - timedelta(days=305*2) )
        test_term = Term.objects.create(season = "Spring",year = 2015, start_date = timezone.now()  - timedelta(days=1),  end_date = timezone.now() + timedelta(days=60) )
        test_term_future = Term.objects.create(season = "Spring",year = 2020, start_date = timezone.now() + timedelta(days=365*5),  end_date = timezone.now() + timedelta(days=(365+65)*5))

        c_code_1 = Course_Code.objects.create(name="Intro To Software Engineering", code="261", credits=4)
        test_course = Course.objects.create(course_code = c_code_1, professor = krutz, term = test_term , section = 1 , capacity = 40 )

        c_code_2 = Course_Code.objects.create(name="Software Engineering Subsystems", code="262", credits=4)
        test_course_2 = Course.objects.create(course_code = c_code_2, professor = krutz, term = test_term , section = 1 , capacity = 40 )

        c_code_3 = Course_Code.objects.create(name="Basket Weaving", code="101", credits=4)
        Course.objects.create(course_code = c_code_3, term = test_term , section = 1 , capacity = 2 )

        c_code_4 = Course_Code.objects.create(name="Software Magic", code="999", credits=6)
        Course.objects.create(course_code = c_code_4, professor = krutz, term = test_term_future , section = 1 , capacity = 35 )

        c_code = Course_Code.objects.create(name="Software Magic", code="777", credits=4)
        Course.objects.create(course_code = c_code, professor = krutz, term = test_term_past , section = 1 , capacity = 35 )

        Prereq.objects.create(prereq_course = c_code_2, course = c_code_1)
        Prereq.objects.create(prereq_course = c_code_4, course = c_code_2)
        Prereq.objects.create(prereq_course = c_code_4, course = c_code_3)

        Course_Session.objects.create(course = test_course, room = test_room, start_time = "12:00", end_time = "14:00", day = "W")

        Course_Session.objects.create(course = test_course_2, room = test_room, start_time = "14:00", end_time = "18:00", day = "M")
        Course_Session.objects.create(course = test_course_2, room = test_room, start_time = "14:00", end_time = "18:00", day = "W")
        Course_Session.objects.create(course = test_course_2, room = test_room, start_time = "14:00", end_time = "18:00", day = "F")

    def test_name(self):
        test_term = Term.objects.get(season = "Spring",year = 2015)
        c_code = Course_Code.objects.get(code="262")
        Course.objects.get(course_code = c_code, term = test_term)

    def test_is_open_true(self):
        NCoriale = Profile.objects.get(user__username = "NCoriale")

        test_term = Term.objects.get(season = "Spring",year = 2015)
        test_course = Course.objects.get(course_code__code = "262", term = test_term)

        NCoriale.enroll_in(test_course)

        self.assertTrue(test_course.is_open())

    def test_is_open_false(self):
        test_term = Term.objects.get(season = "Spring",year = 2015)
        test_course = Course.objects.get(course_code__code = "101", term = test_term)

        MWashburn = Profile.objects.get(user__username = "MWashburn")
        NCoriale = Profile.objects.get(user__username = "NCoriale")

        MWashburn.enroll_in(test_course)
        NCoriale.enroll_in(test_course)

        self.assertFalse(test_course.is_open())

    def test_get_enrollment(self):
        test_term = Term.objects.get(season = "Spring",year = 2015)
        test_course = Course.objects.get(course_code__code = "101", term = test_term)

        self.assertEqual(0, test_course.get_enrollment())

        MWashburn = Profile.objects.get(user__username = "MWashburn")
        NCoriale = Profile.objects.get(user__username = "NCoriale")

        MWashburn.enroll_in(test_course)

        self.assertEqual(1, test_course.get_enrollment())

        NCoriale.enroll_in(test_course)

        self.assertEqual(2, test_course.get_enrollment())

    def test_get_prof(self):
        DKrutz = Profile.objects.get(user__username = "DKrutz")

        test_term = Term.objects.get(season = "Spring",year = 2015)
        test_course = Course.objects.get(course_code__code = "261", term = test_term)

        self.assertEqual(DKrutz.user.first_name + " " + DKrutz.user.last_name, test_course.get_prof())

    def test_get_prof_when_no_proff(self):
        test_term = Term.objects.get(season = "Spring",year = 2015)
        test_course = Course.objects.get(course_code__code = "101", term = test_term)

        self.assertEqual("Staff", test_course.get_prof())

    def test_get_current_courses(self):
        test_term = Term.objects.get(season = "Spring",year = 2015)
        test_course = Course.objects.get(course_code__code = "101", term = test_term)
        test_course_2 = Course.objects.get(course_code__code = "261", term = test_term)
        test_course_3 = Course.objects.get(course_code__code = "262", term = test_term)

        current_course_list = Course.objects.filter(term = test_term)

        self.assertEqual(len(current_course_list),len(Course.get_current_courses()))

        self.assertIn(test_course,Course.get_current_courses())
        self.assertIn(test_course_2,Course.get_current_courses())
        self.assertIn(test_course_3,Course.get_current_courses())

    def test_get_sessions(self):
        test_term = Term.objects.get(season = "Spring",year = 2015)

        test_course = Course.objects.get(course_code__code = "101", term = test_term)
        self.assertEqual(0, len(test_course.get_sessions()))

        test_course = Course.objects.get(course_code__code = "261", term = test_term)
        self.assertEqual(1, len(test_course.get_sessions()))
        self.assertIn(Course_Session.objects.get(course = test_course),test_course.get_sessions())

        test_course = Course.objects.get(course_code__code = "262", term = test_term)
        self.assertEqual(3, len(test_course.get_sessions()))

        course_sessions = Course_Session.objects.filter(course = test_course)

        for session in test_course.get_sessions():
            self.assertIn(session, course_sessions)

    def test_get_prereqs_none(self):
        test_term = Term.objects.get(season = "Spring",year = 2015)
        test_course = Course.objects.get(course_code__code = "261", term = test_term)

        self.assertEqual(0, len(test_course.get_prereqs()))

    def test_get_prereqs_one(self):
        test_term = Term.objects.get(season = "Spring",year = 2015)
        test_course = Course.objects.get(course_code__code = "262", term = test_term)

        self.assertEqual(1, len(test_course.get_prereqs()))

        self.assertIn(Prereq.objects.get(prereq_course__code = "262"), test_course.get_prereqs())

    def test_get_prereqs_two(self):
        test_course = Course.objects.get(course_code__code = "999")

        self.assertEqual(2, len(test_course.get_prereqs()))

        prereq_list = Prereq.objects.filter(prereq_course__code = "999")

        for prereq in test_course.get_prereqs():

            self.assertIn(prereq, prereq_list)

    def test_credits(self):
        test_course = Course.objects.get(course_code__code = "999")
        self.assertEqual(6,test_course.credits())

        test_course = Course.objects.get(course_code__code = "261")
        self.assertEqual(4,test_course.credits())


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

        test_term_past = Term.objects.create(season = "Spring",year = 2013, start_date = timezone.now() - timedelta(days=365*2),  end_date = timezone.now() + - timedelta(days=305*2) )
        test_term = Term.objects.create(season = "Spring",year = 2015, start_date = timezone.now()  - timedelta(days=1),  end_date = timezone.now() + timedelta(days=60) )
        test_term_future = Term.objects.create(season = "Spring",year = 2020, start_date = timezone.now() + timedelta(days=365*5),  end_date = timezone.now() + timedelta(days=(365+65)*5))

        c_code_1 = Course_Code.objects.create(name="Intro To Software Engineering", code="261", credits=4)
        Course.objects.create(course_code = c_code_1, professor = krutz, term = test_term , section = 1 , capacity = 40 )

        c_code_2 = Course_Code.objects.create(name="Software Engineering Subsystems", code="262", credits=4)
        Course.objects.create(course_code = c_code_2, professor = krutz, term = test_term , section = 1 , capacity = 40 )

        c_code = Course_Code.objects.create(name="Software Process", code="256", credits=4)
        Course.objects.create(course_code = c_code, professor = krutz, term = test_term , section = 1 , capacity = 35 )

        c_code = Course_Code.objects.create(name="Personal SE", code="250", credits=4)
        Course.objects.create(course_code = c_code, professor = krutz, term = test_term , section = 1 , capacity = 35 )

        c_code = Course_Code.objects.create(name="Software Magic", code="999", credits=4)
        Course.objects.create(course_code = c_code, professor = krutz, term = test_term_future , section = 1 , capacity = 35 )

        c_code = Course_Code.objects.create(name="Software Magic", code="777", credits=4)
        Course.objects.create(course_code = c_code, professor = krutz, term = test_term_past , section = 1 , capacity = 35 )

        Prereq.objects.create(prereq_course = c_code_2, course = c_code_1)

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

        c_code = Course_Code.objects.get(code="250")
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

    def test_get_terms_up_to(self):

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

        terms = MWashburn.get_terms_up_to(test_term_past)

        self.assertEqual(1, len(terms))

        terms = MWashburn.get_terms_up_to(test_term)

        self.assertEqual(2, len(terms))

        terms = MWashburn.get_terms_up_to(test_term_future)
        self.assertEqual(3, len(terms))

    def test_passed_class_when_no_grade(self):

        MWashburn = Profile.objects.get(user__username = "MWashburn")

        c_code = Course_Code.objects.get(code="261")
        test_course = Course.objects.get(course_code = c_code)

        MWashburn.enroll_in(test_course)

        self.assertFalse(MWashburn.passed_class(c_code))

    def test_passed_class_when_failing_grade(self):

        MWashburn = Profile.objects.get(user__username = "MWashburn")

        c_code = Course_Code.objects.get(code="261")
        test_course = Course.objects.get(course_code = c_code)

        MWashburn.enroll_in(test_course)

        enrolled_in = Enrolled_In.objects.get(student = MWashburn, course__course_code = c_code)

        enrolled_in.grade = GRADE_PASSING - 1

        enrolled_in.save();

        self.assertFalse(MWashburn.passed_class(c_code))

    def test_passed_class_when_minimum_passing_grade(self):

        MWashburn = Profile.objects.get(user__username = "MWashburn")

        c_code = Course_Code.objects.get(code="261")
        test_course = Course.objects.get(course_code = c_code)

        MWashburn.enroll_in(test_course)

        enrolled_in = Enrolled_In.objects.get(student = MWashburn, course__course_code = c_code)

        enrolled_in.grade = GRADE_PASSING

        enrolled_in.save();

        self.assertTrue(MWashburn.passed_class(c_code))

    def test_passed_class_when_perfect_grade(self):

        MWashburn = Profile.objects.get(user__username = "MWashburn")

        c_code = Course_Code.objects.get(code="261")
        test_course = Course.objects.get(course_code = c_code)

        MWashburn.enroll_in(test_course)

        enrolled_in = Enrolled_In.objects.get(student = MWashburn, course__course_code = c_code)

        enrolled_in.grade = GRADE_SCALE

        enrolled_in.save();

        self.assertTrue(MWashburn.passed_class(c_code))

    def test_meets_prerequisites_does_not(self):

        MWashburn = Profile.objects.get(user__username = "MWashburn")

        c_code = Course_Code.objects.get(code="262")
        test_course = Course.objects.get(course_code = c_code)

        self.assertFalse(MWashburn.meets_prerequisites(c_code))

        MWashburn.enroll_in(test_course)

        enrolled_in = Enrolled_In.objects.filter(student = MWashburn, course = test_course)

        self.assertEqual(0, len(enrolled_in))

    def test_meets_prerequisites_does(self):

        MWashburn = Profile.objects.get(user__username = "MWashburn")

        c_code = Course_Code.objects.get(code="261")
        test_course = Course.objects.get(course_code = c_code)

        MWashburn.enroll_in(test_course)

        enrolled_in = Enrolled_In.objects.get(student = MWashburn, course__course_code = c_code)

        enrolled_in.grade = GRADE_SCALE

        enrolled_in.save()

        c_code = Course_Code.objects.get(code="262")
        test_course = Course.objects.get(course_code = c_code)

        self.assertTrue(MWashburn.meets_prerequisites(c_code))

        MWashburn.enroll_in(test_course)

        enrolled_in = Enrolled_In.objects.filter(student = MWashburn, course = test_course)

        self.assertEqual(1, len(enrolled_in))
