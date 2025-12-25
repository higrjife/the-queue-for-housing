from django import forms
from .models import Application, ApplicationDocument

class ApplicantDataForm(forms.ModelForm):
    """Form for basic applicant data"""
    APPLICANT_CHOICES = [
        (False, 'На себя'),  # Applying for themselves
        (True, 'За опекаемого'),  # Applying for a dependent
    ]
    AWARD_CHOICES = [
        ('NO_AWARD', 'Нет наград'),  # No awards
        ('ALTYN_ALQA', 'Алтын алқа'),  # Altyn alqa
        ('KUMIS_ALQA', 'Күміс алқа'),  # Kumis alqa
        ('MOTHER_HEROINE', 'Мать-героиня'),  # Mother heroine
        ('MATERNAL_GLORY_I', 'Орден "Материнская слава" I степени'),  # Maternal glory I
        ('MATERNAL_GLORY_II', 'Орден "Материнская слава" II степени'),  # Maternal glory II
    ]

    CATEGORY_CHOICES = [
        # ('VETERAN', 'Veteran of the Great Patriotic War'),
        ('', 'Выберите категорию'),  # Select category
        ('ORPHAN', 'Сирота или ребенок, оставшийся без попечения родителей'),  # Orphan or child without parental care
        ('LARGE_FAMILY', 'Многодетная семья с наградами'),  # Large family with awards or many children
        ('SOCIAL_VULNERABLE', 'Социально уязвимая группа'),  # Socially vulnerable group
        ('GOVERNMENT_EMPLOYEE', 'Государственный служащий'),  # Government employee
        ('BUDGET_WORKER', 'Работник бюджетной организации'),  # Budget organization worker
        ('MILITARY', 'Военнослужащий'),  # Military personnel
        ('ASTRONAUT', 'Космонавт или кандидат в космонавты'),  # Astronaut or candidate
        ('ELECTED_OFFICIAL', 'Выборное должностное лицо'),  # Elected official
        ('EMERGENCY_HOUSING', 'Гражданин, проживающий в аварийном жилье'),  # Citizen with emergency housing
    ]

    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        widget=forms.Select(attrs={'class': 'w-full p-2 border rounded'}),
        required=True
    )
    is_for_ward = forms.ChoiceField(
        choices=APPLICANT_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'hidden'}),
        required=True
    )
    large_family_awards = forms.ChoiceField(
        choices=AWARD_CHOICES,
        widget=forms.Select(attrs={'class': 'w-full p-2 border rounded'}),
        required=True
    )
    class Meta:
        model = Application
        fields = [
            'is_for_ward',
            'current_residence_condition',
            'monthly_income',
            'current_living_area',
            'current_address',
            'is_homeless',
            'large_family_awards',
            'category',
        ]
        widgets = {
            'current_residence_condition': forms.Select(attrs={'class': 'w-full p-2 border rounded'}),
            'monthly_income': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded'}),
            'current_living_area': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded'}),
            'current_address': forms.Textarea(attrs={'class': 'w-full p-2 border rounded', 'rows': 3}),
            'is_homeless': forms.CheckboxInput(attrs={'class': 'mr-2'}),
        }


class FamilyDataForm(forms.ModelForm):
    """Form for family data and special status"""
    is_single_parent_document = forms.FileField(required=False, widget=forms.FileInput(attrs={'class': 'w-full p-2 border rounded'}))
    is_veteran_document = forms.FileField(required=False, widget=forms.FileInput(attrs={'class': 'w-full p-2 border rounded'}))
    disability_document = forms.FileField(required=False, widget=forms.FileInput(attrs={'class': 'w-full p-2 border rounded'}))
    id_proof_document = forms.FileField(required=False, widget=forms.FileInput(attrs={'class': 'w-full p-2 border rounded'}))
    
    class Meta:
        model = Application
        fields = [
            'is_single_parent',
            'is_veteran',
            'has_disability',
            'disability_details',
            'adults_count',
            'children_count',
            'elderly_count',
        ]
        widgets = {
            'is_single_parent': forms.CheckboxInput(attrs={'class': 'mr-2'}),
            'is_veteran': forms.CheckboxInput(attrs={'class': 'mr-2'}),
            'has_disability': forms.CheckboxInput(attrs={'class': 'mr-2'}),
            'disability_details': forms.Textarea(attrs={'class': 'w-full p-2 border rounded', 'rows': 3}),
            'adults_count': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded', 'min': 1}),
            'children_count': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded', 'min': 0}),
            'elderly_count': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded', 'min': 0}),
        }


class ApplicationSubmissionForm(forms.Form):
    """Form for application submission and notes"""
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'class': 'w-full p-2 border rounded',
        'rows': 4,
        'placeholder': 'Add any additional information here...'
    }))
    confirm_submission = forms.BooleanField(required=True, widget=forms.CheckboxInput(attrs={'class': 'mr-2'}))


def save_application_with_documents(applicant_form, family_form, submission_form, user, application=None):
    """Helper function to save application with related documents"""
    if application:
        # Editing existing application
        for field in applicant_form.fields:
            setattr(application, field, applicant_form.cleaned_data[field])
        for field in family_form.Meta.fields:
            setattr(application, field, family_form.cleaned_data[field])
    else:
        # Creating new application
        application = applicant_form.save(commit=False)
        application.applicant = user
        for field in family_form.Meta.fields:
            setattr(application, field, family_form.cleaned_data[field])

    # Save notes from submission form
    application.notes = submission_form.cleaned_data['notes']
    application.status = 'SUBMITTED'
    application.save()

    # Handle documents
    # ID Proof
    if family_form.cleaned_data.get('remove_id_proof'):
        ApplicationDocument.objects.filter(application=application, document_type='ID_PROOF').delete()
    if family_form.cleaned_data.get('id_proof_document'):
        ApplicationDocument.objects.filter(application=application, document_type='ID_PROOF').delete()
        doc = ApplicationDocument(
            application=application,
            document_type='ID_PROOF',
            file=family_form.cleaned_data['id_proof_document']
        )
        doc.save()

    # Single Parent Proof
    if family_form.cleaned_data.get('is_single_parent'):
        if family_form.cleaned_data.get('remove_single_parent_document'):
            ApplicationDocument.objects.filter(application=application, document_type='SINGLE_PARENT_PROOF').delete()
        if family_form.cleaned_data.get('is_single_parent_document'):
            ApplicationDocument.objects.filter(application=application, document_type='SINGLE_PARENT_PROOF').delete()
            doc = ApplicationDocument(
                application=application,
                document_type='SINGLE_PARENT_PROOF',
                file=family_form.cleaned_data['is_single_parent_document']
            )
            doc.save()
    else:
        ApplicationDocument.objects.filter(application=application, document_type='SINGLE_PARENT_PROOF').delete()

    # Veteran Status
    if family_form.cleaned_data.get('is_veteran'):
        if family_form.cleaned_data.get('remove_veteran_document'):
            ApplicationDocument.objects.filter(application=application, document_type='VETERAN_STATUS').delete()
        if family_form.cleaned_data.get('is_veteran_document'):
            ApplicationDocument.objects.filter(application=application, document_type='VETERAN_STATUS').delete()
            doc = ApplicationDocument(
                application=application,
                document_type='VETERAN_STATUS',
                file=family_form.cleaned_data['is_veteran_document']
            )
            doc.save()
    else:
        ApplicationDocument.objects.filter(application=application, document_type='VETERAN_STATUS').delete()

    # Disability Certificate
    if family_form.cleaned_data.get('has_disability'):
        if family_form.cleaned_data.get('remove_disability_document'):
            ApplicationDocument.objects.filter(application=application, document_type='DISABILITY_CERTIFICATE').delete()
        if family_form.cleaned_data.get('disability_document'):
            ApplicationDocument.objects.filter(application=application, document_type='DISABILITY_CERTIFICATE').delete()
            doc = ApplicationDocument(
                application=application,
                document_type='DISABILITY_CERTIFICATE',
                file=family_form.cleaned_data['disability_document']
            )
            doc.save()
    else:
        ApplicationDocument.objects.filter(application=application, document_type='DISABILITY_CERTIFICATE').delete()

    # Recalculate priority score
    application.calculate_priority()
    return application



class QueueCheckForm(forms.Form):
    iin = forms.CharField(
        label='Individual Identification Number (IIN)',
        max_length=12,
        widget=forms.TextInput(attrs={
            'class': 'w-full border border-gray-300 rounded-lg p-2 mb-4',
            'placeholder': 'Enter your IIN'
        })
    )

    def clean_iin(self):
        iin = self.cleaned_data['iin']
        
        # Validate IIN format (basic validation)
        if not iin.isdigit():
            raise forms.ValidationError("IIN must contain only digits")
        
        if len(iin) != 12:
            raise forms.ValidationError("IIN must be exactly 12 digits")
        
        return iin

class QueueSearchForm(forms.Form):
    iin = forms.CharField(
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
            'placeholder': 'Enter IIN'
        })
    )
    queue_number_from = forms.IntegerField(
        required=False,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
            'placeholder': 'From'
        })
    )
    queue_number_to = forms.IntegerField(
        required=False,
        initial=100,
        widget=forms.NumberInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
            'placeholder': 'To'
        })
    )