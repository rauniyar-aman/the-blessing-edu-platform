from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class UserRole(models.TextChoices):
    SUPER_ADMIN = "SUPER_ADMIN", "Super Admin"
    STAFF = "STAFF", "Staff"
    AGENCY_OWNER = "AGENCY_OWNER", "Agency Owner"
    AGENCY_MANAGER = "AGENCY_MANAGER", "Agency Manager"
    AGENCY_STAFF = "AGENCY_STAFF", "Agency Staff"
    STUDENT = "STUDENT", "Student"


class User(AbstractUser):
    role = models.CharField(max_length=32, choices=UserRole.choices)
    agency = models.ForeignKey(
        "Agency", null=True, blank=True, on_delete=models.SET_NULL, related_name="users"
    )

    def is_internal(self):
        return self.role in {UserRole.SUPER_ADMIN, UserRole.STAFF}


class Agency(models.Model):
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class AgencyRegistrationRequest(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    country = models.CharField(max_length=100)
    contact_name = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20,
        choices=[("PENDING", "Pending"), ("APPROVED", "Approved"), ("REJECTED", "Rejected")],
        default="PENDING",
    )
    created_at = models.DateTimeField(auto_now_add=True)


class AgencySettings(models.Model):
    agency = models.OneToOneField(Agency, on_delete=models.CASCADE, related_name="settings")
    receive_stage_change_emails = models.BooleanField(default=True)
    commission_sections_enabled = models.BooleanField(default=False)


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    phone = models.CharField(max_length=50, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class AgencyStudent(models.Model):
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name="students")
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class University(models.Model):
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=50, choices=[("UK", "UK"), ("USA", "USA")])

    def __str__(self):
        return self.name


class Program(models.Model):
    LEVEL_CHOICES = [("BACHELOR", "Bachelor"), ("MASTER", "Master"), ("PHD", "PhD")]
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name="programs")
    name = models.CharField(max_length=255)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    tuition_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.name} ({self.university.name})"


class ProgramRequirements(models.Model):
    program = models.OneToOneField(Program, on_delete=models.CASCADE, related_name="requirements")
    min_gpa = models.DecimalField(max_digits=4, decimal_places=2, validators=[MinValueValidator(0)])
    english_score = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    gre_score = models.IntegerField(null=True, blank=True)
    gmat_score = models.IntegerField(null=True, blank=True)
    sat_score = models.IntegerField(null=True, blank=True)
    act_score = models.IntegerField(null=True, blank=True)


class Pipeline(models.Model):
    country = models.CharField(max_length=50, choices=[("UK", "UK"), ("USA", "USA")], unique=True)
    name = models.CharField(max_length=255)


class PipelineStage(models.Model):
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name="stages")
    name = models.CharField(max_length=255)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ["order"]


class Application(models.Model):
    SOURCE_CHOICES = [("DIRECT", "Direct"), ("AGENCY", "Agency")]
    STATUS_CHOICES = [("ACTIVE", "Active"), ("CLOSED", "Closed")]

    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    student = models.ForeignKey(
        StudentProfile, null=True, blank=True, on_delete=models.SET_NULL, related_name="applications"
    )
    agency_student = models.ForeignKey(
        AgencyStudent, null=True, blank=True, on_delete=models.SET_NULL, related_name="applications"
    )
    agency = models.ForeignKey(Agency, null=True, blank=True, on_delete=models.SET_NULL)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    country = models.CharField(max_length=50, choices=[("UK", "UK"), ("USA", "USA")])
    intake_month = models.CharField(max_length=20)
    intake_year = models.IntegerField()
    current_stage = models.ForeignKey(
        PipelineStage, null=True, blank=True, on_delete=models.SET_NULL, related_name="applications"
    )
    assigned_staff = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="assigned_applications"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ACTIVE")
    created_at = models.DateTimeField(auto_now_add=True)


class StageHistory(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="stage_history")
    from_stage = models.CharField(max_length=255, blank=True)
    to_stage = models.CharField(max_length=255)
    changed_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    changed_at = models.DateTimeField(auto_now_add=True)


class Note(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="notes")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class DocumentCategory(models.Model):
    name = models.CharField(max_length=255)
    level = models.CharField(
        max_length=20,
        choices=[("ALL", "All"), ("BACHELOR", "Bachelor"), ("MASTER", "Master"), ("PHD", "PhD")],
        default="ALL",
    )
    is_custom = models.BooleanField(default=False)


class Document(models.Model):
    owner_student = models.ForeignKey(
        StudentProfile, null=True, blank=True, on_delete=models.SET_NULL, related_name="documents"
    )
    owner_agency_student = models.ForeignKey(
        AgencyStudent, null=True, blank=True, on_delete=models.SET_NULL, related_name="documents"
    )
    category = models.ForeignKey(DocumentCategory, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)


class DocumentVersion(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="versions")
    file = models.FileField(upload_to="documents/")
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)


class ApplicationDocumentLink(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="document_links")
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    version = models.ForeignKey(DocumentVersion, on_delete=models.CASCADE)


class NoteAttachment(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name="attachments")
    document_version = models.ForeignKey(DocumentVersion, on_delete=models.CASCADE)


class TaskStatus(models.TextChoices):
    TODO = "TODO", "To do"
    IN_PROGRESS = "IN_PROGRESS", "In progress"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"


class Task(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=255)
    assigned_staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=TaskStatus.choices, default=TaskStatus.TODO)
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class TaskAttachment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="attachments")
    document_version = models.ForeignKey(DocumentVersion, on_delete=models.CASCADE)


class AutoAssignmentRule(models.Model):
    university = models.ForeignKey(University, null=True, blank=True, on_delete=models.SET_NULL)
    country = models.CharField(max_length=50, choices=[("UK", "UK"), ("USA", "USA")], blank=True)
    staff = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assignment_rules")
    priority = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["priority"]


class CommissionStructure(models.Model):
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name="commissions")
    level = models.CharField(max_length=20, choices=Program.LEVEL_CHOICES, blank=True)
    country = models.CharField(max_length=50, choices=[("UK", "UK"), ("USA", "USA")])
    percentage = models.DecimalField(max_digits=5, decimal_places=2)


class CommissionStatus(models.TextChoices):
    RECEIVED = "RECEIVED", "Received"
    APPROVED = "APPROVED", "Approved"
    PAID = "PAID", "Paid"


class CommissionRecord(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="commissions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=[("GBP", "GBP"), ("USD", "USD")])
    status = models.CharField(max_length=20, choices=CommissionStatus.choices)
    created_at = models.DateTimeField(auto_now_add=True)


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ("STAGE_CHANGE", "Stage Change"),
        ("ASSIGNMENT_CHANGE", "Assignment Change"),
        ("COMMISSION_STATUS_CHANGE", "Commission Status Change"),
    ]
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    application = models.ForeignKey(Application, on_delete=models.SET_NULL, null=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)


class EmailLog(models.Model):
    to_address = models.EmailField()
    subject = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(default=timezone.now)
