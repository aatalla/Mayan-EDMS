from __future__ import absolute_import

from __future__ import unicode_literals

from django.core.exceptions import PermissionDenied
from django.http import Http404

from rest_framework.permissions import BasePermission

from mayan.apps.acls.models import AccessControlList
from mayan.apps.permissions import Permission


class MayanPermission(BasePermission):
    def has_permission(self, request, view):
        required_permission = getattr(
            view, 'mayan_view_permissions', {}
        ).get(request.method, None)

        if required_permission:
            try:
                Permission.check_permissions(
                    requester=request.user, permissions=required_permission
                )
            except PermissionDenied:
                return False
            else:
                return True
        else:
            return True

    def has_object_permission(self, request, view, obj):
        required_permission = getattr(
            view, 'mayan_object_permissions', {}
        ).get(request.method, None)

        object_permissions_raise_404 = getattr(
            view, 'mayan_object_permissions_raise_404', ()
        )

        if required_permission:
            try:
                if hasattr(view, 'mayan_permission_attribute_check'):
                    AccessControlList.objects.check_access(
                        permissions=required_permission,
                        user=request.user, obj=obj,
                        related=view.mayan_permission_attribute_check
                    )
                else:
                    AccessControlList.objects.check_access(
                        permissions=required_permission, user=request.user,
                        obj=obj
                    )
            except PermissionDenied:
                if request.method in object_permissions_raise_404:
                    raise Http404
                else:
                    return False
            else:
                return True
        else:
            return True
