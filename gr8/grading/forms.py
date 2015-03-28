from django import forms
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

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
        exclude = []
