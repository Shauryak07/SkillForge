from rest_framework import permissions

class JobAccessPermission(permissions.BasePermission):
    message = "Only job owner can modify this job"

    def has_object_permission(self,request,view,obj):
        return obj.client == request.user