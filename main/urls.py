from django.contrib import admin
from django.urls import path,include
from django.conf import settings 
from django.conf.urls.static import static 
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('info', views.info, name='info'),
    path('admin', views.admin, name='admin'),
    path('researcher', views.researcher, name='researcher'),
    path('forest_employee', views.forest_employee, name='forest_employee'),
    path('task', views.task, name='task'),
    path('addtask', views.addtask, name='addtask'),
    path('assigntask', views.assigntask, name='assigntask'),
    path('addanimal', views.addanimal, name='addanimal'),
    path('addcamera', views.addcamera, name='addcamera'),
    path('addresearcher', views.addresearcher, name='addresearcher'),
    path('researcherlist', views.researcherlist, name='researcherlist'),
    #######API#####
    path('gettask', views.give_task.as_view(), name='appdata'),
    path('apptask', views.manage_task.as_view(), name='appdata'),
    path('applogin', views.manage_login.as_view(), name='applogin'),
]