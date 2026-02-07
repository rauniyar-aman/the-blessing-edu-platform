from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AgencySettingsViewSet,
    AgencyStudentViewSet,
    AgencyUserViewSet,
    AgencyVerificationViewSet,
    AgencyViewSet,
    ApplicationViewSet,
    AutoAssignmentRuleViewSet,
    CommissionRecordViewSet,
    CommissionStructureViewSet,
    DocumentCategoryViewSet,
    DocumentViewSet,
    NoteViewSet,
    PipelineStageViewSet,
    PipelineViewSet,
    ProgramRequirementsViewSet,
    ProgramViewSet,
    PublicAgencyRegistrationViewSet,
    StudentSignupViewSet,
    TaskViewSet,
    UniversityViewSet,
)

router = DefaultRouter()
router.register("public/agency-registrations", PublicAgencyRegistrationViewSet, basename="public-agency")
router.register("public/student-signup", StudentSignupViewSet, basename="student-signup")
router.register("admin/agency-registrations", AgencyVerificationViewSet, basename="agency-verification")
router.register("admin/agencies", AgencyViewSet)
router.register("admin/agency-users", AgencyUserViewSet)
router.register("agency/settings", AgencySettingsViewSet, basename="agency-settings")
router.register("agency/students", AgencyStudentViewSet, basename="agency-students")
router.register("universities", UniversityViewSet)
router.register("programs", ProgramViewSet)
router.register("program-requirements", ProgramRequirementsViewSet)
router.register("pipelines", PipelineViewSet)
router.register("pipeline-stages", PipelineStageViewSet)
router.register("applications", ApplicationViewSet, basename="applications")
router.register("notes", NoteViewSet, basename="notes")
router.register("documents", DocumentViewSet, basename="documents")
router.register("document-categories", DocumentCategoryViewSet)
router.register("tasks", TaskViewSet)
router.register("auto-assignment-rules", AutoAssignmentRuleViewSet)
router.register("commission-structures", CommissionStructureViewSet)
router.register("commission-records", CommissionRecordViewSet)

urlpatterns = [path("", include(router.urls))]
