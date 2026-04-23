from rest_framework import permissions

class IsJobOwner(permissions.BasePermission):
    message = "Only job owner can accept bids"

    def has_object_permission(self,request,view,obj):
        return obj.client == request.user