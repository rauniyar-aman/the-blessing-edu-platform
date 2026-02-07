from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import (
    Agency,
    AgencyRegistrationRequest,
    AgencySettings,
    AgencyStudent,
    Application,
    AutoAssignmentRule,
    CommissionRecord,
    CommissionStructure,
    Document,
    DocumentCategory,
    DocumentVersion,
    Note,
    Pipeline,
    PipelineStage,
    Program,
    ProgramRequirements,
    StudentProfile,
    Task,
    University,
    User,
    UserRole,
)
from .permissions import (
    ApplicationObjectPermission,
    DocumentObjectPermission,
    IsInternalOrReadOnly,
    IsAgencyUser,
    IsAgencyOwnerManager,
    IsAgencyOwnerManagerWithCommission,
    IsInternalStaff,
    IsStudent,
    IsSuperAdmin,
    NoteObjectPermission,
)
from .serializers import (
    AgencyRegistrationRequestSerializer,
    AgencySerializer,
    AgencySettingsSerializer,
    AgencyStudentSerializer,
    AgencyUserCreateSerializer,
    ApplicationDetailSerializer,
    ApplicationSerializer,
    AutoAssignmentRuleSerializer,
    CommissionRecordSerializer,
    CommissionStructureSerializer,
    DocumentCategorySerializer,
    DocumentSerializer,
    DocumentUploadSerializer,
    NoteSerializer,
    PipelineSerializer,
    PipelineStageSerializer,
    ProgramRequirementsSerializer,
    ProgramSerializer,
    StageChangeSerializer,
    StudentProfileSerializer,
    TaskSerializer,
    TaskAttachmentUploadSerializer,
    UniversitySerializer,
    UserSerializer,
)


class PublicAgencyRegistrationViewSet(viewsets.ModelViewSet):
    queryset = AgencyRegistrationRequest.objects.all()
    serializer_class = AgencyRegistrationRequestSerializer
    permission_classes = [AllowAny]


class AgencyVerificationViewSet(viewsets.ModelViewSet):
    queryset = AgencyRegistrationRequest.objects.all()
    serializer_class = AgencyRegistrationRequestSerializer
    permission_classes = [IsSuperAdmin]

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        registration = self.get_object()
        registration.status = "APPROVED"
        registration.save(update_fields=["status"])
        agency = Agency.objects.create(name=registration.name, country=registration.country)
        AgencySettings.objects.create(agency=agency)
        return Response({"agency_id": agency.id})


class AgencyViewSet(viewsets.ModelViewSet):
    queryset = Agency.objects.all()
    serializer_class = AgencySerializer
    permission_classes = [IsInternalStaff]


class AgencySettingsViewSet(viewsets.ModelViewSet):
    queryset = AgencySettings.objects.all()
    serializer_class = AgencySettingsSerializer
    permission_classes = [IsAgencyOwnerManager]

    def get_queryset(self):
        return AgencySettings.objects.filter(agency_id=self.request.user.agency_id)


class AgencyUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(role__in=[
        UserRole.AGENCY_OWNER,
        UserRole.AGENCY_MANAGER,
        UserRole.AGENCY_STAFF,
    ])
    serializer_class = UserSerializer
    permission_classes = [IsSuperAdmin]

    @action(detail=False, methods=["post"], serializer_class=AgencyUserCreateSerializer)
    def create_user(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class StudentSignupViewSet(viewsets.ModelViewSet):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        user = User.objects.create_user(
            username=request.data.get("username"),
            email=request.data.get("email"),
            role=UserRole.STUDENT,
            password=request.data.get("password"),
        )
        profile = StudentProfile.objects.create(user=user, phone=request.data.get("phone", ""))
        return Response(StudentProfileSerializer(profile).data, status=status.HTTP_201_CREATED)


class AgencyStudentViewSet(viewsets.ModelViewSet):
    serializer_class = AgencyStudentSerializer
    permission_classes = [IsAgencyUser]

    def get_queryset(self):
        return AgencyStudent.objects.filter(agency_id=self.request.user.agency_id)

    def perform_create(self, serializer):
        serializer.save(agency_id=self.request.user.agency_id)


class UniversityViewSet(viewsets.ModelViewSet):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    permission_classes = [IsInternalOrReadOnly]


class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    permission_classes = [IsInternalOrReadOnly]
    filterset_fields = ["university", "level"]
    search_fields = ["name"]


class ProgramRequirementsViewSet(viewsets.ModelViewSet):
    queryset = ProgramRequirements.objects.all()
    serializer_class = ProgramRequirementsSerializer
    permission_classes = [IsInternalOrReadOnly]


class PipelineViewSet(viewsets.ModelViewSet):
    queryset = Pipeline.objects.all()
    serializer_class = PipelineSerializer
    permission_classes = [IsSuperAdmin]


class PipelineStageViewSet(viewsets.ModelViewSet):
    queryset = PipelineStage.objects.all()
    serializer_class = PipelineStageSerializer
    permission_classes = [IsSuperAdmin]


class ApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = ApplicationSerializer
    permission_classes = [ApplicationObjectPermission]
    filterset_fields = ["country", "status", "assigned_staff"]

    def get_queryset(self):
        user = self.request.user
        if user.role in {UserRole.SUPER_ADMIN, UserRole.STAFF}:
            return Application.objects.all()
        if user.role == UserRole.STUDENT:
            return Application.objects.filter(student__user=user)
        if user.role in {UserRole.AGENCY_OWNER, UserRole.AGENCY_MANAGER, UserRole.AGENCY_STAFF}:
            return Application.objects.filter(agency_id=user.agency_id)
        return Application.objects.none()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ApplicationDetailSerializer
        return ApplicationSerializer

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(
            source="DIRECT" if user.role == UserRole.STUDENT else "AGENCY",
            student=user.student_profile if user.role == UserRole.STUDENT else None,
            agency=user.agency if user.role != UserRole.STUDENT else None,
        )

    @action(detail=True, methods=["post"], serializer_class=StageChangeSerializer)
    def change_stage(self, request, pk=None):
        if request.user.role not in {UserRole.SUPER_ADMIN, UserRole.STAFF}:
            return Response({"detail": "Only internal staff can change stages."}, status=status.HTTP_403_FORBIDDEN)
        application = self.get_object()
        serializer = self.get_serializer(data=request.data, context={"application": application, "request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"status": "stage_updated"})


class NoteViewSet(viewsets.ModelViewSet):
    serializer_class = NoteSerializer
    permission_classes = [NoteObjectPermission]

    def get_queryset(self):
        user = self.request.user
        if user.role in {UserRole.SUPER_ADMIN, UserRole.STAFF}:
            return Note.objects.all()
        if user.role == UserRole.STUDENT:
            return Note.objects.filter(application__student__user=user)
        if user.role in {UserRole.AGENCY_OWNER, UserRole.AGENCY_MANAGER, UserRole.AGENCY_STAFF}:
            return Note.objects.filter(application__agency_id=user.agency_id)
        return Note.objects.none()


class DocumentCategoryViewSet(viewsets.ModelViewSet):
    queryset = DocumentCategory.objects.all()
    serializer_class = DocumentCategorySerializer
    permission_classes = [IsInternalOrReadOnly]
    filterset_fields = [\"level\"]


class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [DocumentObjectPermission]

    def get_queryset(self):
        user = self.request.user
        if user.role in {UserRole.SUPER_ADMIN, UserRole.STAFF}:
            return Document.objects.all()
        if user.role == UserRole.STUDENT:
            return Document.objects.filter(owner_student__user=user)
        if user.role in {UserRole.AGENCY_OWNER, UserRole.AGENCY_MANAGER, UserRole.AGENCY_STAFF}:
            return Document.objects.filter(owner_agency_student__agency_id=user.agency_id)
        return Document.objects.none()

    @action(detail=False, methods=["post"], serializer_class=DocumentUploadSerializer)
    def upload(self, request):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        version = serializer.save()
        return Response({"version_id": version.id})

    def destroy(self, request, *args, **kwargs):
        if request.user.role not in {UserRole.SUPER_ADMIN, UserRole.STAFF}:
            return Response({"detail": "Deletion is not permitted."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsInternalStaff]

    def get_queryset(self):
        return Task.objects.all()

    @action(detail=False, methods=["post"], serializer_class=TaskAttachmentUploadSerializer)
    def upload_attachment(self, request):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        version = serializer.save()
        return Response({"version_id": version.id})


class AutoAssignmentRuleViewSet(viewsets.ModelViewSet):
    queryset = AutoAssignmentRule.objects.all()
    serializer_class = AutoAssignmentRuleSerializer
    permission_classes = [IsSuperAdmin]


class CommissionStructureViewSet(viewsets.ModelViewSet):
    queryset = CommissionStructure.objects.all()
    serializer_class = CommissionStructureSerializer
    permission_classes = [IsInternalStaff | IsAgencyOwnerManagerWithCommission]
    filterset_fields = ["country", "level", "university"]
    search_fields = ["university__name"]


class CommissionRecordViewSet(viewsets.ModelViewSet):
    queryset = CommissionRecord.objects.all()
    serializer_class = CommissionRecordSerializer
    permission_classes = [IsInternalStaff | IsAgencyOwnerManagerWithCommission]
    filterset_fields = ["status", "currency"]

    def get_queryset(self):
        user = self.request.user
        if user.role in {UserRole.SUPER_ADMIN, UserRole.STAFF}:
            return CommissionRecord.objects.all()
        if user.role in {UserRole.AGENCY_OWNER, UserRole.AGENCY_MANAGER}:
            return CommissionRecord.objects.filter(application__agency_id=user.agency_id)
        return CommissionRecord.objects.none()
