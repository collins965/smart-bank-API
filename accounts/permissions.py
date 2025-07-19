from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to view/edit it.
    Assumes the object has a 'user' field or is the User instance itself.
    """
    def has_permission(self, request, view):
        # Allow authenticated users to proceed to object-level check for writes.
        # Allow any request for safe methods (GET, HEAD, OPTIONS).
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Admins can access any object
        if request.user and request.user.is_staff:
            return True

        # If the object itself is the user, or if the object has a 'user' attribute
        # that matches the requesting user.
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return obj == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allow full access to admins, read-only for others.
    """
    def has_permission(self, request, view):
        # Allow GET, HEAD, OPTIONS for any user
        if request.method in permissions.SAFE_METHODS:
            return True

        # Only admins can write
        return request.user and request.user.is_staff


class IsSelfOrAdmin(permissions.BasePermission):
    """
    Allow users to view or edit their own profile, or admins to access any.
    This is very similar to IsOwnerOrAdmin if 'obj' is the user, or 'obj.user' is the user.
    """
    def has_permission(self, request, view):
        # Allow authenticated users to proceed to object-level check for writes.
        # Allow any request for safe methods (GET, HEAD, OPTIONS).
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user and (obj == request.user or request.user.is_staff)


class IsAccountOwner(permissions.BasePermission):
    """
    Only allow access if the user is the owner of the account (i.e., obj.user is the requesting user).
    """
    def has_permission(self, request, view):
        # Must be authenticated to check ownership
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Assumes obj has a 'user' attribute (e.g., Wallet, Profile)
        return obj.user == request.user


class IsSuperUser(permissions.BasePermission):
    """
    Allows access only to superusers.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class IsAuthenticatedAndVerified(permissions.BasePermission):
    """
    Only allow access if the user is authenticated and verified.
    Assumes 'is_verified' is a boolean field on the user's related Profile model.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        try:
            # Check if the user's profile exists and is verified
            return request.user.profile.is_verified
        except: # Catch any exception, including Profile.DoesNotExist
            return False
