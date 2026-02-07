from django.test import TestCase
from rest_framework.test import APIClient

from .models import Agency, AgencyStudent, Application, Program, StudentProfile, University, User, UserRole


class PermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.university = University.objects.create(name="Test Uni", country="UK")
        self.program = Program.objects.create(name="CS", level="BACHELOR", tuition_fee=1000, university=self.university)
        self.agency = Agency.objects.create(name="Agency", country="UK")
        self.staff = User.objects.create_user(username="staff", password="pass", role=UserRole.STAFF)
        self.student_user = User.objects.create_user(username="student", password="pass", role=UserRole.STUDENT)
        self.student_profile = StudentProfile.objects.create(user=self.student_user)
        self.agency_user = User.objects.create_user(
            username="agency", password="pass", role=UserRole.AGENCY_OWNER, agency=self.agency
        )
        self.agency_student = AgencyStudent.objects.create(agency=self.agency, full_name="Agency Student", email="a@example.com")
        self.agency_application = Application.objects.create(
            source="AGENCY",
            agency=self.agency,
            agency_student=self.agency_student,
            program=self.program,
            country="UK",
            intake_month="Sep",
            intake_year=2025,
        )

    def test_student_cannot_access_agency_application(self):
        self.client.force_authenticate(self.student_user)
        response = self.client.get(f"/api/applications/{self.agency_application.id}/")
        self.assertEqual(response.status_code, 404)

    def test_agency_can_access_own_application(self):
        self.client.force_authenticate(self.agency_user)
        response = self.client.get(f"/api/applications/{self.agency_application.id}/")
        self.assertEqual(response.status_code, 200)

    def test_staff_can_access_any_application(self):
        self.client.force_authenticate(self.staff)
        response = self.client.get(f"/api/applications/{self.agency_application.id}/")
        self.assertEqual(response.status_code, 200)
