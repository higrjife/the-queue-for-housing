from django.db import models
from users.models import User
import os, uuid

class Application(models.Model):
    # Category choices based on eligibility groups
    CATEGORY_CHOICES = [
        # ('VETERAN', 'Veteran of the Great Patriotic War'),
        ('ORPHAN', 'Orphan or child without parental care'),
        ('LARGE_FAMILY', 'Large family with awards or many children'),
        ('SOCIAL_VULNERABLE', 'Socially vulnerable group'),
        ('GOVERNMENT_EMPLOYEE', 'Government employee'),
        ('BUDGET_WORKER', 'Budget organization worker'),
        ('MILITARY', 'Military personnel'),
        ('ASTRONAUT', 'Astronaut or candidate'),
        ('ELECTED_OFFICIAL', 'Elected official'),
        ('EMERGENCY_HOUSING', 'Citizen with emergency housing'),
    ]

    # Award choices for large families
    AWARD_CHOICES = [
        ('NO_AWARD', 'Нет наград'),
        ('ALTYN_ALQA', 'Altyn alqa'),
        ('KUMIS_ALQA', 'Kumis alqa'),
        ('MOTHER_HEROINE', 'Mother heroine'),
        ('MATERNAL_GLORY_I', 'Maternal glory I'),
        ('MATERNAL_GLORY_II', 'Maternal glory II'),
    ]

    STATUS_CHOICES = [
        ('SUBMITTED', 'Submitted'),
        ('IN_QUEUE', 'In Queue'),
        ('HOUSING_OFFERED', 'Housing Offered'),
        ('REJECTED_BY_MANAGER', 'Rejected by Manager'),
    ]

    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, null=True, blank=True)
    is_for_ward = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    document_renewal = models.BooleanField(default=False)
    application_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='SUBMITTED')
    submission_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    # Current living conditions
    current_address = models.TextField()
    is_homeless = models.BooleanField(default=False)
    current_residence_condition = models.CharField(max_length=50, choices=[
        ('GOOD', 'Good'),
        ('ADEQUATE', 'Adequate'),
        ('POOR', 'Poor'),
        ('UNSAFE', 'Unsafe'),
    ])

    monthly_income = models.DecimalField(max_digits=10, decimal_places=2)  # Total family monthly income, average over last 12 months
    current_living_area = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    is_veteran = models.BooleanField(default=False)  # Kept for compatibility, but may be redundant with category
    is_single_parent = models.BooleanField(default=False)
    waiting_years = models.PositiveSmallIntegerField(default=0)
    
    has_disability = models.BooleanField(default=False)
    disability_details = models.TextField(blank=True)
    
    adults_count = models.PositiveSmallIntegerField(default=1)
    children_count = models.PositiveSmallIntegerField(default=0)
    elderly_count = models.PositiveSmallIntegerField(default=0)
    
    priority_score = models.IntegerField(default=0)
    
    document_verified = models.BooleanField(default=False)
    
    # Added fields for specific categories
    # veteran_certificate = models.FileField(upload_to='certificates/', null=True, blank=True) # For veterans' benefit certificate
    large_family_awards = models.CharField(max_length=50, choices=AWARD_CHOICES, null=True, blank=True)  # For large family awards
    is_orphan = models.BooleanField(default=False)  # For orphans or children without parental care
    is_without_parental_care = models.BooleanField(default=False)  # For children without parental care
    has_disabled_children = models.BooleanField(default=False)  # For families with disabled children
    has_emergency_housing = models.BooleanField(default=False)  # For emergency housing status
    # emergency_housing_document = models.FileField(upload_to='documents/', null=True, blank=True)  # Proof of emergency housing

    def __str__(self):
        return f"Application {self.application_number} - {self.applicant}"
    
    def calculate_priority(self):
        """Calculate priority score based on various criteria"""
        score = 0
        reference_income = 100000
        
        if self.monthly_income < reference_income:
            income_factor = (reference_income - self.monthly_income) / reference_income
            score += int(income_factor * 20)  # Max 20 points for income
        
        score += self.children_count * 10
        if self.has_disability:
            score += 15
        
        if (self.adults_count + self.children_count + self.elderly_count) > 0 and self.current_living_area:
            space_per_person = self.current_living_area / (self.adults_count + self.children_count + self.elderly_count)
            if space_per_person < 6:
                score += 15
            elif space_per_person < 10:
                score += 10
            elif space_per_person < 15:
                score += 5

        if self.is_veteran:
            score += 10
        
        if self.is_single_parent:
            score += 10
        
        score += self.waiting_years * 5
        
        self.priority_score = score
        self.save(update_fields=['priority_score'])
        return score

    def save(self, *args, **kwargs):
        if not self.application_number:
            last_application = Application.objects.order_by('-id').first()
            if last_application:
                last_id = int(last_application.application_number[3:])
                self.application_number = f"APP{last_id + 1:06d}"
            else:
                self.application_number = "APP000001"

        super().save(*args, **kwargs)

class ApplicationHistory(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='history')
    previous_status = models.CharField(max_length=30, choices=Application.STATUS_CHOICES)
    new_status = models.CharField(max_length=30, choices=Application.STATUS_CHOICES)
    change_date = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.application.application_number}: {self.previous_status} → {self.new_status}"

class ApplicationDocument(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=50, choices=[
        ('ID_PROOF', 'ID Proof'),
        ('INCOME_STATEMENT', 'Income Statement'),
        ('DISABILITY_CERTIFICATE', 'Disability Certificate'),
        ('VETERAN_STATUS', 'Veteran Status'),
        ('SINGLE_PARENT_PROOF', 'Single Parent Proof'),
        ('OTHER', 'Other'),
    ])
    file = models.FileField(upload_to='application_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    document_name = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.application.application_number} - {self.get_document_type_display()}"

    def save(self, *args, **kwargs):
        """Ensure unique file name and document name."""
        if not self.document_name:
            base_name, ext = os.path.splitext(self.file.name)
            unique_filename = f"{uuid.uuid4().hex}{ext}"
            self.file.name = unique_filename

            # Ensure uniqueness of document_name in the same application
            count = 1
            new_name = base_name
            while ApplicationDocument.objects.filter(application=self.application, document_name=new_name).exists():
                new_name = f"{base_name}_{count}"
                count += 1

            self.document_name = new_name  # Set unique document name

        super().save(*args, **kwargs)
