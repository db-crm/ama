from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User

from .models import process_assessment

from django import forms 
from django.forms.widgets import PasswordInput, TextInput

from django import forms
from django.urls import reverse
from django.shortcuts import redirect
from .models import process_assessment, department, division, area
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Div
from formtools.wizard.views import SessionWizardView
import datetime




# - Register/Create a new user 

class CreateUserForm(UserCreationForm):
    class Meta:

        model = User
        fields = ['username','password1','password2']

# -Login a user 
class LoginForm(AuthenticationForm):

    username = forms.CharField(widget=TextInput())
    password = forms.CharField(widget=PasswordInput())


# - Create a record
class GeneralInfoForm(forms.ModelForm):
    class Meta:
        model = process_assessment
        fields = ['process_assessment_date', 'process_department', 'process_division', 'process_area', 'process_description', 'process_lead', 'process_status']
        widgets = {
            'process_assessment_date': forms.DateInput(attrs={'type': 'date'}),
            'process_status': forms.Select(choices=process_assessment.STATUS_CHOICES),
            'process_division': forms.Select(attrs={'class': 'dependent-dropdown'}),
            'process_area': forms.Select(attrs={'class': 'dependent-dropdown'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['process_division'].queryset = division.objects.all()
        self.fields['process_area'].queryset = area.objects.all()

        if self.data.get('process_department'):
            try:
                department_id = int(self.data.get('process_department'))
                self.fields['process_division'].queryset = division.objects.filter(division_department_id=department_id)
            except (ValueError, TypeError):
                pass

        if self.data.get('process_division'):
            try:
                division_id = int(self.data.get('process_division'))
                self.fields['process_area'].queryset = area.objects.filter(area_division_id=division_id)
            except (ValueError, TypeError):
                pass
        # Add this block to handle initial data
        elif self.instance.pk:
            self.fields['process_division'].queryset = self.instance.process_department.division_set.order_by('division_name')
            self.fields['process_area'].queryset = self.instance.process_division.area_set.order_by('area_name')

    def clean(self):
        cleaned_data = super().clean()
        if 'process_lead' in cleaned_data:
            self.process_lead_value = cleaned_data['process_lead']
        return cleaned_data


class ProcessNameForm(forms.ModelForm):
    class Meta:
        model = process_assessment
        fields = ['process_name_c', 'process_name_s', 'process_name_n']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['process_name_n'].initial = "N/A"

class TriggeringEventsForm(forms.ModelForm):
    class Meta:
        model = process_assessment
        fields = ['process_trigger_c', 'process_trigger_s', 'process_trigger_n']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['process_trigger_n'].initial = "N/A"

class ToolsUsedForm(forms.ModelForm):
    class Meta:
        model = process_assessment
        fields = ['process_tools_c', 'process_tools_s', 'process_tools_n']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['process_tools_n'].initial = "N/A"

class ProcessStepsForm(forms.ModelForm):
    class Meta:
        model = process_assessment
        fields = ['process_steps_c', 'process_steps_s', 'process_steps_n']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['process_steps_n'].initial = "N/A"

class ActorsForm(forms.ModelForm):
    class Meta:
        model = process_assessment
        fields = ['process_actors_c', 'process_actors_s', 'process_actors_n']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['process_actors_n'].initial = "N/A"

class ObjectiveForm(forms.ModelForm):
    class Meta:
        model = process_assessment
        fields = ['process_objective_c', 'process_objective_s', 'process_objective_n']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['process_objective_n'].initial = "N/A"

class GradeForm(forms.ModelForm):
    class Meta:
        model = process_assessment
        fields = ['process_grade']

class RecommendationsForm(forms.ModelForm):
    class Meta:
        model = process_assessment
        fields = ['process_proposal']
        widgets = {
            'process_proposal': forms.Textarea(attrs={
                'rows': 5, 
                'class': 'bullet-point-input',
                'placeholder': 'Enter recommendations (one per line)'
            }),
        }
        



# - Update a record
class UpdateRecordForm(forms.ModelForm):

    class Meta:

        model = process_assessment
        fields = [

            # General Info
            'process_assessment_date',
            'process_department', 
            'process_division', 
            'process_area', 
            'process_description',
                          # Process Breakdown:

                # Name -> How do you refer to this process?
            'process_name_c',
            'process_name_s',
            'process_name_n',
                        # Triggering Events -> What causes this process to be executed?
            'process_trigger_c',
            'process_trigger_s',
            'process_trigger_n',

                         # Tools Used -> What are the tools/systems used to carry out the process?
            'process_tools_c',
            'process_tools_s',
            'process_tools_n',

                        # Process Steps / Activities -> What are the steps involved in this process?
            'process_steps_c',
            'process_steps_s',
            'process_steps_n',

                        # Actors -> Who are the main participants in this process?
            'process_actors_c',
            'process_actors_s',
            'process_actors_n',
                         # Objective  -> What is the objective of the process?
            'process_objective_c',
            'process_objective_s',
            'process_objective_n',
                                    # Process Satisfaction Grade
            'process_grade',

            # Proposed improvements/changes: 
            'process_proposal',
        ]

        widgets = {
                        # General Info
            'process_assessment_date': forms.DateInput(attrs={'type':'date'})

        }


        labels = {
            # General Info
            'process_assessment_date': 'Day Assessed:',
            'process_department': 'Department', 
            'process_division': 'Division', 
            'process_area': 'Area', 
            'process_description': 'Description',
                        # Process Breakdown:

                # Name -> How do you refer to this process?
            'process_name_c': 'How do you refer to this process?',
                         # Triggering Events -> What causes this process to be executed?
            'process_trigger_c': 'What causes this process to be executed?',
                      # Tools Used -> What are the tools/systems used to carry out the process?
            'process_tools_c':'What are the tools/systems used to carry out the process?',
                         # Process Steps / Activities -> What are the steps involved in this process?
            'process_steps_c':'What are the steps involved in this process?',

                        # Actors -> Who are the main participants in this process?
            'process_actors_c':'Who are the main participants in this process?',
                         # Objective  -> What is the objective of the process?
            'process_objective_c':'What is the objective of the process?',
                        # Process Satisfaction Grade
            'process_grade':'Grade given by supervisor:',

            # Proposed improvements/changes: 
            'process_proposal': 'Proposed improvements/changes',



        }
 
