from django.db import models
# from django_mysql.models import ListCharField
# from picklefield.fields import PickledObjectField
from django.contrib.postgres.fields import ArrayField
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles

LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
STYLE_CHOICES = sorted([(item, item) for item in get_all_styles()])

class Animal(models.Model):
    animal_id= models.CharField(max_length=200)
    animal_name= models.CharField(max_length=200)
    animal_info= models.CharField(max_length=500)
    latitude = ArrayField(models.FloatField())
    longitude = ArrayField(models.FloatField())
    def __str__(self):
        return self.animal_name

class Login(models.Model):
	username = models.CharField(max_length=200)
	password = models.CharField(max_length=200)
	def __str__(self):
		return self.username

class Camera(models.Model):
    camera_id = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()
    status = models.CharField(max_length=200)
    def __str__(self):
        return self.camera_id

class Tasks(models.Model):
	task_id = models.CharField(max_length=200)
	task_info = models.CharField(max_length=200)
	deadline = models.DateField()
	task_from = models.CharField(max_length=200)
	task_to = models.CharField(max_length=200)
	status = models.CharField(max_length=200)
	def __str__(self):
		return self.task_id

class Logs(models.Model):
    camera_id = models.CharField(max_length=200)
    time = models.CharField(max_length=200)
    action = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()
    def __str__(self):
        return self.camera_id

class Status(models.Model):
    camera_id = models.CharField(max_length=200)
    time = models.CharField(max_length=200)
    action = models.CharField(max_length=200)
    def __str__(self):
        return self.camera_id

class Researcher(models.Model):
    researcher_id = models.CharField(max_length=200)
    researcher_name = models.CharField(max_length=200)
    animal = ArrayField(models.CharField(max_length=200))
    experience = models.CharField(max_length=200)
    qualification = models.CharField(max_length=200)
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    def __str__(self):
        return self.researcher_name

class Forest_employee(models.Model):
    area = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    empid = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    def __str__(self):
        return self.name

class Report(models.Model):
    empid = models.CharField(max_length=200)
    description = models.CharField(max_length=1000)
    image = models.BinaryField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    def __str__(self):
        return self.empid

class Task_Description(models.Model):
    task_id = models.CharField(max_length=200)
    description = models.CharField(max_length=1000)
    image = models.BinaryField()
    def __str__(self):
        return self.task_id

class Division_range(models.Model):
    division_id = models.CharField(max_length=200)
    range_id = models.CharField(max_length=200)
    def __str__(self):
        return self.division_id

class Range_beat(models.Model):
    range_id = models.CharField(max_length=200)
    beat_id = models.CharField(max_length=200)
    def __str__(self):
        return self.range_id
