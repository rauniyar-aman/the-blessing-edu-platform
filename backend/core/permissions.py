from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import UserRole, Application


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == UserRole.SUPER_ADMIN


class IsInternalStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in {
            UserRole.SUPER_ADMIN,
            UserRole.STAFF,
        }


class IsAgencyUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in {
            UserRole.AGENCY_OWNER,
            UserRole.AGENCY_MANAGER,
            UserRole.AGENCY_STAFF,
        }


class IsAgencyOwnerManager(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return IsAgencyUser().has_permission(request, view)
        return request.user.is_authenticated and request.user.role in {
            UserRole.AGENCY_OWNER,
            UserRole.AGENCY_MANAGER,
        }


class IsAgencyOwnerManagerWithCommission(BasePermission):
    def has_permission(self, request, view):
        if request.method not in SAFE_METHODS:
            return False
        if not request.user.is_authenticated or request.user.role not in {
            UserRole.AGENCY_OWNER,
            UserRole.AGENCY_MANAGER,
        }:
            return False
        agency = getattr(request.user, "agency", None)
        return bool(agency and getattr(agency, "settings", None) and agency.settings.commission_sections_enabled)


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == UserRole.STUDENT


class IsInternalOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role in {
            UserRole.SUPER_ADMIN,
            UserRole.STAFF,
        }


class ApplicationObjectPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role in {UserRole.SUPER_ADMIN, UserRole.STAFF}:
            return True
        if request.user.role == UserRole.STUDENT:
            return obj.student and obj.student.user_id == request.user.id
        if request.user.role in {UserRole.AGENCY_OWNER, UserRole.AGENCY_MANAGER, UserRole.AGENCY_STAFF}:
            return obj.agency_id == request.user.agency_id
        return False


class NoteObjectPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        application = obj.application
        return ApplicationObjectPermission().has_object_permission(request, view, application)


class DocumentObjectPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role in {UserRole.SUPER_ADMIN, UserRole.STAFF}:
            return True
        if request.user.role == UserRole.STUDENT:
            return obj.owner_student and obj.owner_student.user_id == request.user.id
        if request.user.role in {UserRole.AGENCY_OWNER, UserRole.AGENCY_MANAGER, UserRole.AGENCY_STAFF}:
            return obj.owner_agency_student and obj.owner_agency_student.agency_id == request.user.agency_id
        return False
