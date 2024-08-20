from django.db import models

# Department Choices for Data Validation
class department(models.Model):

    # Meta Data
    creation_date = models.DateTimeField(auto_now_add=True)
    # General Info
    department_name = models.CharField(max_length=100)

    def __str__(self):
        return self.department_name

# Division Choices for Data Validation
class division(models.Model):

    # Meta Data
    creation_date = models.DateTimeField(auto_now_add=True)
    # General Info
    division_department = models.ForeignKey(department, on_delete=models.PROTECT,verbose_name ='Department')
    division_name = models.CharField(max_length=100)

    def __str__(self):
        return self.division_name
    
# Area
class area(models.Model):

    # Meta Data
    creation_date = models.DateTimeField(auto_now_add=True)
    # General Info
    area_department = models.ForeignKey(department, on_delete=models.PROTECT,verbose_name ='Department')
    area_division = models.ForeignKey(division, on_delete=models.PROTECT,verbose_name ='Division')
    area_name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.area_name
    
# Process Assessment
class process_assessment(models.Model):


    # Meta Data
    creation_date = models.DateTimeField(auto_now_add=True)

    # General Info
    process_assessment_date = models.DateField('Date Assessed')
    process_department = models.ForeignKey(department, on_delete=models.PROTECT, verbose_name ='Department')
    process_division = models.ForeignKey(division, on_delete=models.PROTECT, verbose_name ='Division')
    process_area = models.ForeignKey(area,on_delete=models.PROTECT,verbose_name ='Area')
    process_description = models.TextField('Description')
    process_lead = models.TextField('Process Lead',null=True)

    STATUS_CHOICES = (
        ("Deprecated", "Deprecated"),
        ("On-going", "On-going"),
        ("Implementing", "Implementing"),
    )    
    process_status= models.CharField(max_length=255, choices=STATUS_CHOICES, default="On-going") 
    
    

    # Process Breakdown:

        # Name -> How do you refer to this process?
    process_name_c = models.CharField('Comments',max_length=100)
    process_name_s = models.CharField('Source',max_length=100)
    process_name_n = models.TextField('Next Steps')

        # Triggering Events -> What causes this process to be executed?
    process_trigger_c = models.TextField('Comments')
    process_trigger_s = models.CharField('Source',max_length=100)
    process_trigger_n = models.TextField('Next Steps')

        # Tools Used -> What are the tools/systems used to carry out the process?
    process_tools_c = models.TextField('Comments')
    process_tools_s = models.CharField('Source',max_length=100)
    process_tools_n = models.TextField('Next Steps')

        # Process Steps / Activities -> What are the steps involved in this process?
    process_steps_c = models.TextField('Comments')
    process_steps_s = models.CharField('Source',max_length=100)
    process_steps_n = models.TextField('Next Steps')

        # Actors -> Who are the main participants in this process?
    process_actors_c = models.TextField('Comments')
    process_actors_s = models.CharField('Source',max_length=100)
    process_actors_n = models.TextField('Next Steps')

        # Objective  -> What is the objective of the process?
    process_objective_c = models.TextField('Comments')
    process_objective_s = models.CharField('Source',max_length=100)
    process_objective_n = models.TextField('Next Steps')


    # Process Satisfaction Grade
    process_grade = models.CharField('Grade given by Supervisor',max_length=3)


    # Proposed improvements/changes: 
    process_proposal = models.TextField('Recommendations')

    def __str__(self):
        return self.process_name_c 


