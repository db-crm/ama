from django.db import migrations, models
import django.db.models.deletion

def convert_process_lead(apps, schema_editor):
    ProcessAssessment = apps.get_model('web_ama', 'process_assessment')
    TechnologyStaff = apps.get_model('web_ama', 'technology_staff')
    
    for assessment in ProcessAssessment.objects.all():
        # Create TechnologyStaff for process_lead if it doesn't exist
        if assessment.process_lead:
            lead, created = TechnologyStaff.objects.get_or_create(
                name=assessment.process_lead,
                defaults={
                    'department': assessment.process_department,
                    'division': assessment.process_division,
                    'area': assessment.process_area,
                    'email': 'default@example.com',
                    'phone': '0000000000',
                    'position': 'Unknown'
                }
            )
            assessment.new_process_lead = lead
        
        # Create TechnologyStaff for process_lead_bk if it doesn't exist
        if assessment.process_lead_bk:
            lead_bk, created = TechnologyStaff.objects.get_or_create(
                name=assessment.process_lead_bk,
                defaults={
                    'department': assessment.process_department,
                    'division': assessment.process_division,
                    'area': assessment.process_area,
                    'email': 'default@example.com',
                    'phone': '0000000000',
                    'position': 'Unknown'
                }
            )
            assessment.new_process_lead_bk = lead_bk
        
        assessment.save()

class Migration(migrations.Migration):

    dependencies = [
        ('web_ama', '0004_technology_staff'),  # Make sure this matches your actual migration history
    ]

    operations = [
        migrations.AddField(
            model_name='process_assessment',
            name='new_process_lead',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='led_processes', to='web_ama.technology_staff', verbose_name='Process Lead'),
        ),
        migrations.AddField(
            model_name='process_assessment',
            name='new_process_lead_bk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='backup_led_processes', to='web_ama.technology_staff', verbose_name='Process Lead Backup'),
        ),
        migrations.RunPython(convert_process_lead),
        migrations.RemoveField(
            model_name='process_assessment',
            name='process_lead',
        ),
        migrations.RemoveField(
            model_name='process_assessment',
            name='process_lead_bk',
        ),
        migrations.RenameField(
            model_name='process_assessment',
            old_name='new_process_lead',
            new_name='process_lead',
        ),
        migrations.RenameField(
            model_name='process_assessment',
            old_name='new_process_lead_bk',
            new_name='process_lead_bk',
        ),
    ]