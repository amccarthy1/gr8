from django import forms
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms.extras.widgets import SelectDateWidget
import datetime

class GradeForm(forms.ModelForm):

    class Meta:
        model = Enrolled_In
        fields = ['grade']

class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        exclude = ('user',)

class UserForm(UserCreationForm):
    """
    Allows the creation of a new user, with fields:
        - username
        - first_name
        - last_name
        - email
        - password1
        - password2
    """
    #All fields are required
    email = forms.EmailField(label='Email', required=True)
    first_name = forms.CharField(label='First Name', required=True)
    last_name = forms.CharField(label='Last Name', required=True)
    
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password1", "password2"]


class SuperUserForm(UserCreationForm):
    """
    Allows the creation of a new user, with fields:
        - username
        - first_name
        - last_name
        - email
        - password1
        - password2
        - is_staff
    """
    #All fields are required
    email = forms.EmailField(label='Email', required=True)
    first_name = forms.CharField(label='First Name', required=True)
    last_name = forms.CharField(label='Last Name', required=True)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password1", "password2","is_staff"]


class RoomForm(forms.ModelForm):

    class Meta:
        model = Room
        fields = ["name"]

class CourseForm(forms.ModelForm):

    class Meta:
        model = Course
        exclude = ["course_code", "section"]

class CourseCodeForm(forms.ModelForm):

    # uppercase all course codes
    def clean_code(self):
        return self.cleaned_data['code'].upper()

    class Meta:
        model = Course_Code
        fields = ["code", "name", "credits"]

class TermForm(forms.ModelForm):

    start_date = forms.DateField(widget=SelectDateWidget, initial=datetime.date.today())

    end_date = forms.DateField(widget=SelectDateWidget, initial=datetime.date.today())

    class Meta:
        model = Term;
        exclude = ["year"]

    def clean_end_date(self):
        if self.cleaned_data["start_date"] > self.cleaned_data["end_date"]:
            raise ValidationError("End date cannot be less than the start date")
        if (self.cleaned_data["end_date"] - self.cleaned_data["start_date"]).days > 365:
            raise ValidationError("Terms should not be longer than a year")
        return self.cleaned_data["end_date"]
