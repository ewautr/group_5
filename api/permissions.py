from rest_framework  import permissions
from banking_app.utils import is_employee


class IsEmployeeOrReadOnly(object):
    def has_object_permission(self, request, view, obj):
        #readf only permissions are allowed for anyone
        if  request.method in permissions.SAFE_METHODS:
            return True

        #write permissions are only allowed to the employee
        return is_employee(request.user)