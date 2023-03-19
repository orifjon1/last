from rest_framework.permissions import BasePermission


class IsDirector(BasePermission):

    def has_permission(self, request, view):
        if request.method == 'POST' and request.user.status == 'director':
            return True
        elif request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return False
