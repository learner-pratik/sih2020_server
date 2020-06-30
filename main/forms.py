from .models import Tasks,Animal,Researcher,Camera,Logs,Login
from django import forms

class addtaskform(forms.ModelForm):
	class Meta:
		model = Tasks
		exclude = ()

class addanimalform(forms.ModelForm):
	class Meta:
		model = Animal
		exclude = ()

class addresearcherform(forms.ModelForm):
	class Meta:
		model = Researcher
		exclude = ()

class addcameraform(forms.ModelForm):
	class Meta:
		model = Camera
		exclude = ()

class addlogsform(forms.ModelForm):
	class Meta:
		model = Logs
		exclude = ()

class adduserform(forms.ModelForm):
	class Meta:
		model = Login
		exclude = ()