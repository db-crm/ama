from django.shortcuts import render, redirect,get_object_or_404
from .forms import *

from django.contrib.auth.models import auth
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import department,division,area,process_assessment

from formtools.wizard.views import SessionWizardView

from django.http import HttpResponse,JsonResponse
from django.core.exceptions import ValidationError
import json
from django.core.serializers.json import DjangoJSONEncoder

from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from django.forms.models import model_to_dict

from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
import os
from django.conf import settings
import base64


from reportlab.lib import colors

import csv
import xlsxwriter

from reportlab.lib.pagesizes import letter, inch, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# Add these imports at the top of your views.py file
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import ProcessAssessmentSerializer
from django.db.models import Count, Avg
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required(login_url='my_login')
def delete_record(request, pk):
    record = get_object_or_404(process_assessment, id=pk)
    
    if request.method == 'GET':
        record.delete()
        messages.success(request, "Record deleted successfully.")
        return redirect('dashboard')
    
    return redirect('dashboard')

def home(request):
    return render(request,'web_ama/index.html')

#  - Register 

def register(request):

    form = CreateUserForm

    if request.method == "POST":

         form =  CreateUserForm(request.POST)

         if form.is_valid():
             
             form.save()

             return redirect('my_login')

    context = {'registerform':form}
    return render(request, 'web_ama/register.html', context=context)

# - Login a user 

def my_login(request):

    form = LoginForm()

    if request.method == "POST":

        form = LoginForm(request, data=request.POST)

        if form.is_valid():

            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:

                auth.login(request,user)

                return redirect('dashboard')

    context = {'loginform': form}

    return render(request, 'web_ama/my_login.html', context=context)

@login_required(login_url='my_login')
def dashboard(request):
    assessments = process_assessment.objects.all().order_by('creation_date')
    departments = department.objects.all()
    divisions = division.objects.all()
    areas = area.objects.all()

    # Calculate KPIs
    total_assessments = assessments.count()
    one_month_ago = timezone.now() - relativedelta(months=1)
    assessments_this_month = assessments.filter(process_assessment_date__gte=one_month_ago).count()
   
    context = {
        'assessments': assessments,
        'departments': departments,
        'divisions': divisions,
        'areas': areas,
        'total_assessments': total_assessments,
        'assessments_this_month': assessments_this_month,
    }
    return render(request, 'web_ama/dashboard.html', context)

@login_required(login_url='my_login')
def get_filtered_assessments(request):
    search_term = request.GET.get('search', '')
    department_id = request.GET.get('department', '')
    division_id = request.GET.get('division', '')
    area_id = request.GET.get('area', '')
    items_per_page = int(request.GET.get('items_per_page', 10))
    page_number = int(request.GET.get('page', 1))

    assessments = process_assessment.objects.all().order_by('-creation_date')

    if search_term:
        assessments = assessments.filter(
            Q(process_name_c__icontains=search_term) |
            Q(process_description__icontains=search_term)
        )
    
    if department_id:
        assessments = assessments.filter(process_department_id=department_id)
    
    if division_id:
        assessments = assessments.filter(process_division_id=division_id)
    
    if area_id:
        assessments = assessments.filter(process_area_id=area_id)

    # Calculate KPIs
    total_assessments = assessments.count()
    one_month_ago = timezone.now() - relativedelta(months=1)
    assessments_this_month = assessments.filter(process_assessment_date__gte=one_month_ago).count()

    paginator = Paginator(assessments, items_per_page)
    page_obj = paginator.get_page(page_number)

    assessments_data = [{
        'id': assessment.id,
        'creation_date': assessment.creation_date.strftime('%Y-%m-%d %H:%M:%S'),
        'process_assessment_date': assessment.process_assessment_date.strftime('%Y-%m-%d'),
        'process_department': str(assessment.process_department),
        'process_division': str(assessment.process_division),
        'process_area': str(assessment.process_area),
        'process_description': assessment.process_description,
        'process_lead': str(assessment.process_lead),
        'process_status': assessment.process_status,
        'process_name_c': assessment.process_name_c,
        'process_name_s': assessment.process_name_s,
        'process_name_n': assessment.process_name_n,
        'process_trigger_c': assessment.process_trigger_c,
        'process_trigger_s': assessment.process_trigger_s,
        'process_trigger_n': assessment.process_trigger_n,
        'process_tools_c': assessment.process_tools_c,
        'process_tools_s': assessment.process_tools_s,
        'process_tools_n': assessment.process_tools_n,
        'process_steps_c': assessment.process_steps_c,
        'process_steps_s': assessment.process_steps_s,
        'process_steps_n': assessment.process_steps_n,
        'process_actors_c': assessment.process_actors_c,
        'process_actors_s': assessment.process_actors_s,
        'process_actors_n': assessment.process_actors_n,
        'process_objective_c': assessment.process_objective_c,
        'process_objective_s': assessment.process_objective_s,
        'process_objective_n': assessment.process_objective_n,
        'process_grade': assessment.process_grade,
        'process_proposal': assessment.process_proposal,
    } for assessment in page_obj]

    return JsonResponse({
        'assessments': assessments_data,
        'total_pages': paginator.num_pages,
        'current_page': page_number,
        'kpis': {
            'total_assessments': total_assessments,
            'assessments_this_month': assessments_this_month,
        }
    })

def get_all_divisions_areas(request):
    try:
        divisions = list(division.objects.all().values('id', 'division_name', 'division_department_id'))
        areas = list(area.objects.all().values('id', 'area_name', 'area_division_id'))
        # print(divisions)
        return JsonResponse({
            'divisions': divisions,
            'areas': areas
        })
    except Exception as e:
        print(f"Error in get_all_divisions_areas: {str(e)}")  # For debugging
        return JsonResponse({'error': 'Internal server error'}, status=500)

@method_decorator(login_required(login_url='my_login'), name='dispatch')
class CreateRecordView(SessionWizardView):
    form_list = [GeneralInfoForm, ProcessNameForm, TriggeringEventsForm, ToolsUsedForm, 
                 ProcessStepsForm, ActorsForm, ObjectiveForm, GradeForm, RecommendationsForm]
    template_name = 'web_ama/create_record.html'

    def get_form_initial(self, step):
        initial = super().get_form_initial(step)
        if step == '0':  # First step
            initial['process_assessment_date'] = datetime.date.today()
        elif step != '0':  # For all steps after the first one
            # Get the process_lead value from the first step
            first_step_data = self.get_cleaned_data_for_step('0')
            if first_step_data and 'process_lead' in first_step_data:
                process_lead = first_step_data['process_lead']
                # Prepopulate all fields ending with "_s" with the process_lead value
                if step == '1':
                    initial['process_name_s'] = process_lead
                elif step == '2':
                    initial['process_trigger_s'] = process_lead
                elif step == '3':
                    initial['process_tools_s'] = process_lead
                elif step == '4':
                    initial['process_steps_s'] = process_lead
                elif step == '5':
                    initial['process_actors_s'] = process_lead
                elif step == '6':
                    initial['process_objective_s'] = process_lead      
        return initial

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        step_titles = [
            'Enter General Info',
            'How do you refer to this process?',
            'What causes this process to be executed?',
            'What are the tools/systems used to carry out the process?',
            'What are the steps involved in this process?',
            'Who are the main participants in this process?',
            'What is the objective of the process?',
            'How do you rate this process based on the following graph?',
            'Proposed Changes'
        ]
        context.update({
            'step_title': step_titles[int(self.steps.current)],
            'form_data_json': json.dumps(self.get_serializable_form_data(), cls=DjangoJSONEncoder)
        })
        return context

    def get_serializable_form_data(self):
        data = {}
        for step in range(self.steps.index + 1):
            form = self.get_form(step=str(step), data=self.storage.get_step_data(step))
            if form.is_valid():
                step_data = form.cleaned_data
            else:
                step_data = form.data
            
            # Convert model instances to dictionaries
            for key, value in step_data.items():
                if hasattr(value, '_meta'):  # Check if it's a model instance
                    data[key] = model_to_dict(value, fields=['id', 'name'])
                else:
                    data[key] = value
        return data

    def done(self, form_list, **kwargs):
        form_data = {}
        for form in form_list:
            form_data.update(form.cleaned_data)
        
        
        process_assessment_obj = process_assessment.objects.create(**form_data)
        return redirect("dashboard")
    
    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() == 'get' and (request.GET.get('department') or request.GET.get('division')):
            return self.ajax_response(request)
        return super().dispatch(request, *args, **kwargs)

    def ajax_response(self, request):
        if 'department' in request.GET:
            department_id = request.GET.get('department')
            divisions = division.objects.filter(division_department_id=department_id).values('id', 'division_name')
            return JsonResponse(list(divisions), safe=False)
        elif 'division' in request.GET:
            division_id = request.GET.get('division')
            areas = area.objects.filter(area_division_id=division_id).values('id', 'area_name')
            return JsonResponse(list(areas), safe=False)
        return JsonResponse({'error': 'Invalid request'}, status=400)

    
# @login_required(login_url='my_login') 
# def create_record(request):
#     form = CreateRecordForm

#     if request.method == "POST":
#         form  = CreateRecordForm(request.POST)

#         if form.is_valid():
#             form.save()

#             return redirect("dashboard")

#     context = {'createrecordform':form}
#     return render(request, 'web_ama/create_record.html', context=context)



# - Update a record
@login_required(login_url='my_login')
def update_record(request, pk):

    record = process_assessment.objects.get(id=pk)

    form = UpdateRecordForm(instance=record)

    if request.method == "POST":

        form = UpdateRecordForm(request.POST,instance=record)

        if form.is_valid():
            form.save()

            return redirect('dashboard')
        
    context = {'update_record_form': form}

    return render(request, 'web_ama/update_record.html', context = context)


# - View a singular record


@login_required(login_url='my_login')
def singular_record(request,pk):
    
    def format_li(line):
        """Format the proposals as bullet points."""
        lines = line.split('\n')
        return [line.strip() for line in lines if line.strip()]
    process = process_assessment.objects.get(id=pk)


    # Format as li
    process.process_trigger_c = format_li( process.process_trigger_c)
    process.process_tools_c = format_li( process.process_tools_c)
    process.process_steps_c = format_li( process.process_steps_c)
    process.process_actors_c = format_li( process.process_actors_c )
    process.process_objective_c = format_li( process.process_objective_c )
    process.process_proposal = format_li( process.process_proposal)

    context= {'assessment':process}

    return render(request, 'web_ama/view_record.html',context=context)



# - Delete a record
@login_required(login_url='my_login')
def delete_record(request, pk):
    record = get_object_or_404(process_assessment, id=pk)
    
    if request.method == 'GET':
        record.delete()
        messages.success(request, "Record deleted successfully.")
        return redirect('dashboard')
    
    return redirect('dashboard')


# - Generate a PDF

def generate_pdf(request,pk):
    # Create a Bystream buffer
    buf=io.BytesIO()
    # create canvas
    c = canvas.Canvas(buf,pagesize=letter,bottomup=0)
    # create a text object
    textob = c.beginText()
    textob.setTextOrigin(inch,inch)
    textob.setFont("Helvetica", 14)

    

    # designate our model
    assessments= process_assessment.objects.all()
    record = process_assessment.objects.get(id=pk)

    # Add some lines of text
    lines = [ ]

    for assessment in assessments:
        if assessment.id == record.id:

    # for assessment in assessments:

            lines.append(str(assessment.id))
            lines.append(str(assessment.process_name_c))
            lines.append(str(assessment.creation_date))
            lines.append(str(assessment.process_assessment_date))
            lines.append(str(assessment.process_department))
            lines.append(str(assessment.process_division))
            lines.append(str(assessment.process_area))
            lines.append(assessment.process_description)
            lines.append(assessment.process_name_s)
            lines.append(assessment.process_name_n)
            lines.append(assessment.process_trigger_c)
            lines.append(assessment.process_trigger_s)
            lines.append(assessment.process_trigger_n)
            lines.append(assessment.process_tools_c)
            lines.append(assessment.process_tools_s)
            lines.append(assessment.process_tools_n)
            lines.append(assessment.process_steps_c )
            lines.append(assessment.process_steps_s)
            lines.append(assessment.process_steps_n)
            lines.append(assessment.process_actors_c)
            lines.append(assessment.process_actors_s)
            lines.append(assessment.process_actors_n)
            lines.append(assessment.process_objective_c)
            lines.append(assessment.process_objective_s)
            lines.append(assessment.process_objective_n)
            lines.append(assessment.process_grade)
            lines.append(assessment.process_proposal)

    # loop
    for line in lines:
        textob.textLine(line)
    # finish
    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)


    # return something
    return  FileResponse(buf, as_attachment=True,filename='process_assessment.pdf')
    

# PDF Export 
@login_required(login_url='my_login')


def export_process_assessment_pdf(request, pk):


    def format_li(line):
        """Format the proposals as bullet points."""
        lines = line.split('\n')
        return [line.strip() for line in lines if line.strip()]

    template = get_template('web_ama/p_assessment_e_temp.html')
    process = process_assessment.objects.get(pk=pk)
    
    # Format the proposals


    # Format as li
    process.process_trigger_c = format_li( process.process_trigger_c)
    process.process_tools_c = format_li( process.process_tools_c)
    process.process_steps_c = format_li( process.process_steps_c)
    process.process_actors_c = format_li( process.process_actors_c )
    process.process_objective_c = format_li( process.process_objective_c )
    process.process_proposal = format_li( process.process_proposal)
    
    # Read the image and encode it
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'L-RMTS-Logo.png')
    with open(logo_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()

    # Read the CSS file
    css_path = os.path.join(settings.BASE_DIR, 'static', 'css', 'pdf.css')
    with open(css_path, 'r') as css_file:
        css_content = css_file.read()
    
    context = {
        'process': process,
        'logo': f"data:image/png;base64,{encoded_string}",
        'css_content': css_content,
    }
    
    html = template.render(context)
    result = BytesIO()
    
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return HttpResponse('Error generating PDF', status=400)

# - Log out an user

def user_logout(request):
    auth.logout(request)
    return redirect("my_login")





# - Export Table PDF
@login_required(login_url='my_login')
def export_table_pdf(request):
    # Get filter parameters
    search_term = request.GET.get('search', '')
    department_id = request.GET.get('department', '')
    division_id = request.GET.get('division', '')
    area_id = request.GET.get('area', '')

    # Filter assessments
    assessments = process_assessment.objects.all()
    if search_term:
        assessments = assessments.filter(
            Q(process_name_c__icontains=search_term) |
            Q(process_description__icontains=search_term)
        )
    if department_id:
        assessments = assessments.filter(process_department_id=department_id)
    if division_id:
        assessments = assessments.filter(process_division_id=division_id)
    if area_id:
        assessments = assessments.filter(process_area_id=area_id)

    # Order assessments
    assessments = assessments.order_by('id')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="process_assessments.pdf"'
    
    # Create the PDF object using SimpleDocTemplate
    doc = SimpleDocTemplate(response, pagesize=landscape(letter), topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Add title
    styles = getSampleStyleSheet()
    title = Paragraph("Process Assessments", styles['Title'])
    elements.append(title)
    elements.append(Paragraph("<br/>", styles['Normal']))  # Add some space after the title
    
    # Create table data
    data = [['ID', 'Department', 'Division', 'Area', 'Process Name', 'Process Lead', 'Date Assessed', 'Created On']]
    for assessment in assessments:
        data.append([
            str(assessment.id),
            str(assessment.process_department),
            str(assessment.process_division),
            str(assessment.process_area),
            assessment.process_lead,
            assessment.process_name_c,
            assessment.process_assessment_date.strftime('%Y-%m-%d'),
            assessment.creation_date.strftime('%Y-%m-%d %H:%M')
        ])
    
    # Create the table
    table = Table(data)
    
    # Style the table (unchanged)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])
    table.setStyle(style)
    
    # Add the table to elements
    elements.append(table)
    
    # Build the PDF
    doc.build(elements)
    return response

# - Export Table Excel
@login_required(login_url='my_login')
def export_table_excel(request):
    # Get filter parameters
    search_term = request.GET.get('search', '')
    department_id = request.GET.get('department', '')
    division_id = request.GET.get('division', '')
    area_id = request.GET.get('area', '')

    # Filter assessments
    assessments = process_assessment.objects.all()
    if search_term:
        assessments = assessments.filter(
            Q(process_name_c__icontains=search_term) |
            Q(process_description__icontains=search_term)
        )
    if department_id:
        assessments = assessments.filter(process_department_id=department_id)
    if division_id:
        assessments = assessments.filter(process_division_id=division_id)
    if area_id:
        assessments = assessments.filter(process_area_id=area_id)

    # Create a workbook and add a worksheet.
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()

    # Write headers
    headers = [
        'ID', 'Creation Date', 'Date Assessed', 'Department', 'Division', 'Area',
        'Description', 'Process Lead', 'Status', 'Name (Comments)', 'Name (Source)',
        'Name (Next Steps)', 'Trigger (Comments)', 'Trigger (Source)', 'Trigger (Next Steps)',
        'Tools (Comments)', 'Tools (Source)', 'Tools (Next Steps)', 'Steps (Comments)',
        'Steps (Source)', 'Steps (Next Steps)', 'Actors (Comments)', 'Actors (Source)',
        'Actors (Next Steps)', 'Objective (Comments)', 'Objective (Source)',
        'Objective (Next Steps)', 'Grade', 'Recommendations'
    ]
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)

    # Write data rows
    for row, assessment in enumerate(assessments, start=1):
        worksheet.write(row, 0, assessment.id)
        worksheet.write(row, 1, assessment.creation_date.strftime('%Y-%m-%d %H:%M:%S'))
        worksheet.write(row, 2, assessment.process_assessment_date.strftime('%Y-%m-%d'))
        worksheet.write(row, 3, str(assessment.process_department))
        worksheet.write(row, 4, str(assessment.process_division))
        worksheet.write(row, 5, str(assessment.process_area))
        worksheet.write(row, 6, assessment.process_description)
        worksheet.write(row, 7, assessment.process_lead)
        worksheet.write(row, 8, assessment.process_status)
        worksheet.write(row, 9, assessment.process_name_c)
        worksheet.write(row, 10, assessment.process_name_s)
        worksheet.write(row, 11, assessment.process_name_n)
        worksheet.write(row, 12, assessment.process_trigger_c)
        worksheet.write(row, 13, assessment.process_trigger_s)
        worksheet.write(row, 14, assessment.process_trigger_n)
        worksheet.write(row, 15, assessment.process_tools_c)
        worksheet.write(row, 16, assessment.process_tools_s)
        worksheet.write(row, 17, assessment.process_tools_n)
        worksheet.write(row, 18, assessment.process_steps_c)
        worksheet.write(row, 19, assessment.process_steps_s)
        worksheet.write(row, 20, assessment.process_steps_n)
        worksheet.write(row, 21, assessment.process_actors_c)
        worksheet.write(row, 22, assessment.process_actors_s)
        worksheet.write(row, 23, assessment.process_actors_n)
        worksheet.write(row, 24, assessment.process_objective_c)
        worksheet.write(row, 25, assessment.process_objective_s)
        worksheet.write(row, 26, assessment.process_objective_n)
        worksheet.write(row, 27, assessment.process_grade)
        worksheet.write(row, 28, assessment.process_proposal)

    workbook.close()

    # Create the HttpResponse object with Excel header
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=process_assessments.xlsx'
    response.write(output.getvalue())
    return response




class ProcessAssessmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = process_assessment.objects.all()
    serializer_class = ProcessAssessmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['process_department', 'process_division']
    search_fields = ['process_name_c', 'process_description']

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        
        # Calculate KPIs
        total_assessments = process_assessment.objects.count()
        one_month_ago = timezone.now() - relativedelta(months=1)
        assessments_this_month = process_assessment.objects.filter(creation_date__gte=one_month_ago).count()
        avg_assessments_per_dept = process_assessment.objects.values('process_department').annotate(count=Count('id')).aggregate(Avg('count'))['count__avg'] or 0

        response.data['kpis'] = {
            'total_assessments': total_assessments,
            'assessments_this_month': assessments_this_month,
            'avg_assessments_per_dept': avg_assessments_per_dept,
        }

        return response


# - Test

@login_required(login_url='my_login')
def test(request):

    return render(request, 'web_ama/test.html')
