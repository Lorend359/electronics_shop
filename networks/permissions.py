"""Права доступа для API торговой сети."""

from rest_framework.permissions import BasePermission


class IsActiveStaff(BasePermission):
    """Разрешение: только активные сотрудники."""

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and request.user.is_active and request.user.is_staff
        )
