from django import forms
from time_tracker.models import Developer
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class DeveloperCreationForm(forms.ModelForm):
    class Meta:
        model = Developer
        fields = '__all__'

    # def clean_user(self):
    #     return self.cleaned_data['user']

    def clean_avatar(self):
        return self.cleaned_data['avatar']


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'is_active',
            'is_staff',
            'password1',
            'password2'
        )

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']

        user.save()
        return user
