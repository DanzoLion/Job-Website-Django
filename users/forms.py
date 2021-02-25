from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Account, Profile, Invite


class AccountRegisterForm(UserCreationForm):                # in models.py we have our class Account we develop our form based on fields, two important fields: is_employee + is_employer
    CHOICES = [('is_employee', 'Employee'), ('is_employer', 'Employer')]
    user_types = forms.CharField(label="User Type", widget=forms.RadioSelect(choices=CHOICES))

    class Meta:
        model = Account                                     # where Account is from .models # our reference when registering a user
        fields = ['email', 'first_name', 'last_name']       # password fields are brought in by UserCreationForm so we don't need to register those here

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ('user',)                                  # we don't need the user field as we are creating an update form not add new user form
        widgets = {
            'birth_day': forms.DateInput(attrs={'type':'date'})     # now that we have a date-picker we need to create a new class in views.py
        }


class InviteEmployeeForm(forms.ModelForm):
    class Meta:
        model = Invite
        fields = ('date', 'message')

        widgets = {
            'date':forms.DateInput(attrs={'type':'date'})
        }