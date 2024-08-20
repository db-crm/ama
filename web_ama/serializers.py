# serializers.py

from rest_framework import serializers
from .models import process_assessment

class ProcessAssessmentSerializer(serializers.ModelSerializer):
    process_department = serializers.StringRelatedField()
    process_division = serializers.StringRelatedField()
    process_area = serializers.StringRelatedField()

    class Meta:
        model = process_assessment
        fields = ['id', 'process_department', 'process_division', 'process_area', 
                  'process_name_c', 'process_assessment_date', 'creation_date']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['process_assessment_date'] = instance.process_assessment_date.strftime('%Y-%m-%d')
        representation['creation_date'] = instance.creation_date.strftime('%Y-%m-%d %H:%M:%S')
        return representation