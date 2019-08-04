from django import forms
from .models import Comment, Log, Task, Project


class AddCommentToTaskForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = '__all__'


class AddTimeToTaskForm(forms.ModelForm):
    class Meta:
        model = Log
        fields = '__all__'


class CreateTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = '__all__'


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'description')


class EditTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(EditTaskForm, self).__init__(*args, **kwargs)
        self.fields['creator'].widget.attrs['disabled'] = True
        self.fields['creator'].required = False

    def clean_creator(self):
        if self.instance and self.instance.pk:
            return self.instance.creator
        else:
            return self.cleaned_data['creator']
