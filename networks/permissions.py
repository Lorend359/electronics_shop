"""Права доступа для API торговой сети."""

from rest_framework.permissions import BasePermission


class IsActiveUser(BasePermission):
    """Доступ к API только для активных пользователей."""

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_active)
