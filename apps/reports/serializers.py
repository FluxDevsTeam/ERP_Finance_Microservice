from rest_framework import serializers
from .models import ReportTemplate, GeneratedReport


class ReportTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportTemplate
        fields = '__all__'
        read_only_fields = ('tenant', 'branch', 'created_by', 'updated_by',
                          'created_at', 'updated_at')


class GeneratedReportSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source='template.name', read_only=True)
    
    class Meta:
        model = GeneratedReport
        fields = '__all__'
        read_only_fields = ('tenant', 'branch', 'created_by', 'generated_at',
                          'report_data')