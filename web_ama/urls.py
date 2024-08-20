from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProcessAssessmentViewSet
from . import views
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'api/assessments', ProcessAssessmentViewSet)


urlpatterns = [

    path('', views.home, name=""),

    path('register', views.register, name="register"),
    path('my_login', views.my_login, name="my_login"),
    path('user_logout', views.user_logout, name ="user_logout"),

    # CURD
    path('dashboard', views.dashboard, name ="dashboard"),
    path('get-filtered-assessments/', views.get_filtered_assessments, name='get_filtered_assessments'),
    path('get-all-divisions-areas/', views.get_all_divisions_areas, name='get_all_divisions_areas'),
  
    path('create-assessment/', views.CreateRecordView.as_view(), name='create_assessment'),


    path('update_record/<int:pk>', views.update_record, name ="update_record"),
    path('record/<int:pk>', views.singular_record, name='record'),
    path('delete_record/<int:pk>', views.delete_record, name='delete_record'),
    path('generate_pdf/<int:pk>', views.export_process_assessment_pdf, name='generate_pdf'),
    path('test', views.test, name='test'),

    path('export_pdf/', views.export_table_pdf, name='export_pdf'),
    path('export_excel/', views.export_table_excel, name='export_excel'),


    path('', include(router.urls)),
   
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)




