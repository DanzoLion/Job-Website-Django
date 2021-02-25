from django import forms
from .models import *




class CreateJobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'company', 'location', 'job_type', 'category', 'description']            # these are option fields brought in from ./jobs/models.py
        widgets = {'job_type': forms.RadioSelect}                                                   # where we decide to use a radio button here


class ApplyJobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = []                                                                                 # class SearchJobView assigns employee to the empty list for us


class UpdateJobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'company', 'location', 'job_type', 'category', 'description']            # these are option fields brought in from ./jobs/models.py
        widgets = {'job_type': forms.RadioSelect}