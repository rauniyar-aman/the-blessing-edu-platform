from django.db import transaction
from rest_framework import serializers

from .models import (
    Agency,
    AgencyRegistrationRequest,
    AgencySettings,
    AgencyStudent,
    Application,
    ApplicationDocumentLink,
    AutoAssignmentRule,
    CommissionRecord,
    CommissionStructure,
    Document,
    DocumentCategory,
    DocumentVersion,
    Note,
    NoteAttachment,
    Pipeline,
    PipelineStage,
    Program,
    ProgramRequirements,
    StudentProfile,
    Task,
    TaskAttachment,
    University,
    User,
)
from .services import auto_assign_application, create_default_tasks, record_assignment_change, record_stage_change, record_commission_status_change


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "agency"]


class AgencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Agency
        fields = ["id", "name", "country", "created_at"]


class AgencySettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgencySettings
        fields = ["receive_stage_change_emails", "commission_sections_enabled"]


class AgencyRegistrationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgencyRegistrationRequest
        fields = ["id", "name", "email", "country", "contact_name", "status", "created_at"]
        read_only_fields = ["status", "created_at"]


class StudentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = StudentProfile
        fields = ["id", "user", "phone", "nationality", "created_at"]


class AgencyStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgencyStudent
        fields = ["id", "agency", "full_name", "email", "phone", "created_at"]
        read_only_fields = ["created_at"]


class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = ["id", "name", "country"]


class ProgramSerializer(serializers.ModelSerializer):
    university = UniversitySerializer(read_only=True)
    university_id = serializers.PrimaryKeyRelatedField(
        queryset=University.objects.all(), source="university", write_only=True
    )

    class Meta:
        model = Program
        fields = ["id", "name", "level", "tuition_fee", "university", "university_id"]


class ProgramRequirementsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramRequirements
        fields = [
            "id",
            "program",
            "min_gpa",
            "english_score",
            "gre_score",
            "gmat_score",
            "sat_score",
            "act_score",
        ]


class PipelineStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PipelineStage
        fields = ["id", "name", "order"]


class PipelineSerializer(serializers.ModelSerializer):
    stages = PipelineStageSerializer(many=True, read_only=True)

    class Meta:
        model = Pipeline
        fields = ["id", "country", "name", "stages"]


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = [
            "id",
            "source",
            "student",
            "agency_student",
            "agency",
            "program",
            "country",
            "intake_month",
            "intake_year",
            "current_stage",
            "assigned_staff",
            "status",
            "created_at",
        ]
        read_only_fields = ["assigned_staff", "created_at"]

    def validate(self, attrs):
        user = self.context["request"].user
        if user.role == "STUDENT":
            if attrs.get("agency_student") or attrs.get("agency"):
                raise serializers.ValidationError("Direct students cannot set agency fields.")
        if user.role in {"AGENCY_OWNER", "AGENCY_MANAGER", "AGENCY_STAFF"}:
            if not attrs.get("agency_student"):
                raise serializers.ValidationError("Agency applications require an agency student.")
            if attrs["agency_student"].agency_id != user.agency_id:
                raise serializers.ValidationError("Agency student must belong to your agency.")
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        application = Application.objects.create(**validated_data)
        staff = auto_assign_application(application)
        if staff:
            record_assignment_change(application, staff, request.user)
        create_default_tasks(application)
        return application


class ApplicationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = [
            "id",
            "source",
            "student",
            "agency_student",
            "agency",
            "program",
            "country",
            "intake_month",
            "intake_year",
            "current_stage",
            "assigned_staff",
            "status",
            "created_at",
            "stage_history",
        ]
        depth = 1


class StageChangeSerializer(serializers.Serializer):
    stage_id = serializers.PrimaryKeyRelatedField(queryset=PipelineStage.objects.all())

    def save(self, **kwargs):
        application = self.context["application"]
        actor = self.context["request"].user
        record_stage_change(application, self.validated_data["stage_id"], actor)
        return application


class DocumentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentCategory
        fields = ["id", "name", "level", "is_custom"]


class DocumentVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentVersion
        fields = ["id", "file", "uploaded_by", "uploaded_at"]
        read_only_fields = ["uploaded_by", "uploaded_at"]


class DocumentSerializer(serializers.ModelSerializer):
    versions = DocumentVersionSerializer(many=True, read_only=True)

    class Meta:
        model = Document
        fields = ["id", "name", "category", "owner_student", "owner_agency_student", "created_at", "versions"]
        read_only_fields = ["created_at"]


class DocumentUploadSerializer(serializers.Serializer):
    document_id = serializers.PrimaryKeyRelatedField(queryset=Document.objects.all(), required=False)
    category = serializers.PrimaryKeyRelatedField(queryset=DocumentCategory.objects.all(), required=False)
    name = serializers.CharField(required=False)
    agency_student_id = serializers.PrimaryKeyRelatedField(
        queryset=AgencyStudent.objects.all(), required=False, write_only=True
    )
    file = serializers.FileField()

    def validate(self, attrs):
        user = self.context["request"].user
        if not attrs.get("document_id") and not attrs.get("name"):
            raise serializers.ValidationError("Provide document_id or name for new document")
        if user.role in {"AGENCY_OWNER", "AGENCY_MANAGER", "AGENCY_STAFF"}:
            if not attrs.get("agency_student_id"):
                raise serializers.ValidationError("Agency uploads require agency_student_id.")
            if attrs["agency_student_id"].agency_id != user.agency_id:
                raise serializers.ValidationError("Agency student must belong to your agency.")
        if user.role == "STUDENT" and attrs.get("agency_student_id"):
            raise serializers.ValidationError("Students cannot upload on behalf of agency students.")
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        request = self.context["request"]
        user = request.user
        agency_student = validated_data.get("agency_student_id")
        document = validated_data.get("document_id")
        if not document:
            document = Document.objects.create(
                name=validated_data.get("name"),
                category=validated_data.get("category"),
                owner_student=user.student_profile if hasattr(user, "student_profile") else None,
                owner_agency_student=agency_student,
            )
        version = DocumentVersion.objects.create(
            document=document,
            file=validated_data["file"],
            uploaded_by=user,
        )
        return version


class ApplicationDocumentLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationDocumentLink
        fields = ["id", "application", "document", "version"]


class NoteAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteAttachment
        fields = ["id", "document_version"]


class NoteSerializer(serializers.ModelSerializer):
    attachments = NoteAttachmentSerializer(many=True, read_only=True)
    files = serializers.ListField(child=serializers.FileField(), write_only=True, required=False)

    class Meta:
        model = Note
        fields = ["id", "application", "author", "content", "created_at", "attachments", "files"]
        read_only_fields = ["author", "created_at", "attachments"]

    @transaction.atomic
    def create(self, validated_data):
        files = validated_data.pop("files", [])
        request = self.context["request"]
        note = Note.objects.create(author=request.user, **validated_data)
        for file in files:
            document = Document.objects.create(
                name=file.name,
                owner_student=note.application.student,
                owner_agency_student=note.application.agency_student,
            )
            version = DocumentVersion.objects.create(
                document=document,
                file=file,
                uploaded_by=request.user,
            )
            NoteAttachment.objects.create(note=note, document_version=version)
            ApplicationDocumentLink.objects.create(
                application=note.application,
                document=document,
                version=version,
            )
        return note


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            "id",
            "application",
            "title",
            "assigned_staff",
            "due_date",
            "status",
            "comments",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class TaskAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAttachment
        fields = ["id", "task", "document_version"]


class TaskAttachmentUploadSerializer(serializers.Serializer):
    task_id = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all())
    file = serializers.FileField()
    name = serializers.CharField(required=False)

    @transaction.atomic
    def create(self, validated_data):
        request = self.context["request"]
        task = validated_data["task_id"]
        application = task.application
        document = Document.objects.create(
            name=validated_data.get("name") or validated_data["file"].name,
            owner_student=application.student,
            owner_agency_student=application.agency_student,
        )
        version = DocumentVersion.objects.create(
            document=document,
            file=validated_data["file"],
            uploaded_by=request.user,
        )
        TaskAttachment.objects.create(task=task, document_version=version)
        ApplicationDocumentLink.objects.create(
            application=application,
            document=document,
            version=version,
        )
        return version


class AutoAssignmentRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutoAssignmentRule
        fields = ["id", "university", "country", "staff", "priority"]


class CommissionStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommissionStructure
        fields = ["id", "university", "level", "country", "percentage"]


class CommissionRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommissionRecord
        fields = ["id", "application", "amount", "currency", "status", "created_at"]
        read_only_fields = ["created_at"]

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        record_commission_status_change(instance, self.context["request"].user)
        return instance


class AgencyUserCreateSerializer(serializers.Serializer):
    agency_id = serializers.PrimaryKeyRelatedField(queryset=Agency.objects.all())
    username = serializers.CharField()
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=["AGENCY_OWNER", "AGENCY_MANAGER", "AGENCY_STAFF"])
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            role=validated_data["role"],
            agency=validated_data["agency_id"],
            password=validated_data["password"],
        )
