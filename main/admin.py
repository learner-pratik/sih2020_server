from django.contrib import admin

from .models import Animal,Login,Camera,Tasks,Logs,Researcher,Forest_employee,Status

admin.site.register(Login)
admin.site.register(Animal)
admin.site.register(Camera)
admin.site.register(Tasks)
admin.site.register(Logs)
admin.site.register(Status)
admin.site.register(Researcher)
admin.site.register(Forest_employee)