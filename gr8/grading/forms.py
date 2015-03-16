from django import forms
from .models import *
from django.contrib.auth.models import User

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
