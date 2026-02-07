from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone

from .models import (
    AuditLog,
    AutoAssignmentRule,
    Application,
    Pipeline,
    Task,
    UserRole,
)


def send_stage_change_email(application, recipients, new_stage):
    if not recipients:
        return
    subject = f"Application stage updated: {application.program.name}"
    body = (
        f"The application for {application.program.name} moved to stage: {new_stage}."
    )
    send_mail(subject, body, None, recipients)


def auto_assign_application(application):
    rules = AutoAssignmentRule.objects.all()
    for rule in rules:
        if rule.university and rule.university_id == application.program.university_id:
            return rule.staff
    for rule in rules:
        if rule.country and rule.country == application.country:
            return rule.staff
    default_rule = rules.filter(university__isnull=True, country=\"\").first() or rules.filter(university__isnull=True, country__isnull=True).first()
    return default_rule.staff if default_rule else None


def create_default_tasks(application):
    template_country = application.country
    tasks = []
    if template_country == "UK":
        tasks = ["Collect documents", "Submit UCAS", "Follow up offer"]
    if template_country == "USA":
        tasks = ["Collect documents", "Submit application", "Track I-20"]
    for title in tasks:
        Task.objects.create(application=application, title=title, assigned_staff=application.assigned_staff)


@transaction.atomic
def record_stage_change(application, new_stage, actor):
    from_stage = application.current_stage.name if application.current_stage else ""
    application.current_stage = new_stage
    application.save(update_fields=["current_stage"])
    application.stage_history.create(
        from_stage=from_stage,
        to_stage=new_stage.name,
        changed_by=actor,
    )
    AuditLog.objects.create(
        action="STAGE_CHANGE",
        actor=actor,
        application=application,
        metadata={"from": from_stage, "to": new_stage.name},
    )
    recipients = []
    if application.source == "DIRECT" and application.student:
        recipients.append(application.student.user.email)
    if application.source == "AGENCY":
        recipients.append("admin@blessing-edu.local")
        if application.assigned_staff:
            recipients.append(application.assigned_staff.email)
        if application.agency and getattr(application.agency, "settings", None):
            if application.agency.settings.receive_stage_change_emails:
                recipients.extend([user.email for user in application.agency.users.all()])
    send_stage_change_email(application, recipients, new_stage.name)


def record_assignment_change(application, new_staff, actor):
    previous = application.assigned_staff_id
    application.assigned_staff = new_staff
    application.save(update_fields=["assigned_staff"])
    AuditLog.objects.create(
        action="ASSIGNMENT_CHANGE",
        actor=actor,
        application=application,
        metadata={"from": previous, "to": new_staff.id if new_staff else None},
    )


def record_commission_status_change(commission, actor):
    AuditLog.objects.create(
        action="COMMISSION_STATUS_CHANGE",
        actor=actor,
        application=commission.application,
        metadata={"status": commission.status, "amount": str(commission.amount)},
    )
