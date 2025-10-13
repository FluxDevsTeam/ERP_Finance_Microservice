from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import ReportTemplate, GeneratedReport
from .serializers import ReportTemplateSerializer, GeneratedReportSerializer
from .permissions import IsReportOwner
from .enhanced_report_generator import ReportGenerator


class ReportTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = ReportTemplateSerializer
    permission_classes = [IsAuthenticated, IsReportOwner]

    def get_queryset(self):
        return ReportTemplate.objects.filter(
            tenant=self.request.tenant_id,
            branch=self.request.branch_id
        )

    def perform_create(self, serializer):
        serializer.save(
            tenant=self.request.tenant_id,
            branch=self.request.branch_id,
            created_by=self.request.user.id
        )


class GeneratedReportViewSet(viewsets.ModelViewSet):
    serializer_class = GeneratedReportSerializer
    permission_classes = [IsAuthenticated, IsReportOwner]

    def get_queryset(self):
        return GeneratedReport.objects.filter(
            tenant=self.request.tenant_id,
            branch=self.request.branch_id
        )

    def perform_create(self, serializer):
        generator = ReportGenerator(
            tenant_id=self.request.tenant_id,
            branch_id=self.request.branch_id,
            start_date=serializer.validated_data.get('start_date'),
            end_date=serializer.validated_data.get('end_date')
        )

        template = serializer.validated_data['template']
        
        report_methods = {
            'balance_sheet': generator.get_balance_sheet,
            'income_statement': generator.get_income_statement,
            'cash_flow': generator.get_cash_flow,
            'trial_balance': generator.get_trial_balance,
            'accounts_receivable': lambda: generator.get_accounts_aging('receivable'),
            'accounts_payable': lambda: generator.get_accounts_aging('payable'),
            'budget_variance': generator.get_budget_variance,
            'expense_analysis': generator.get_expense_analysis,
            'revenue_analysis': generator.get_revenue_analysis,
            'tax_report': generator.get_tax_report,
            'bank_reconciliation': generator.get_bank_reconciliation,
            'department_pl': generator.get_department_pl,
            'project_costing': generator.get_project_costing,
            'fixed_assets': generator.get_fixed_assets_register
        }
        
        report_method = report_methods.get(template.report_type)
        if not report_method:
            raise ValueError(f"Unknown report type: {template.report_type}")
            
        report_data = report_method()

        serializer.save(
            tenant=self.request.tenant_id,
            branch=self.request.branch_id,
            created_by=self.request.user.id,
            report_data=report_data
        )

    @action(detail=True, methods=['post'])
    def regenerate(self, request, pk=None):
        report = self.get_object()
        generator = ReportGenerator(
            tenant_id=self.request.tenant_id,
            branch_id=self.request.branch_id,
            start_date=report.start_date,
            end_date=report.end_date
        )

        template = report.template
        if template.report_type == 'balance_sheet':
            report_data = generator.get_balance_sheet()
        elif template.report_type == 'income_statement':
            report_data = generator.get_income_statement()
        elif template.report_type == 'cash_flow':
            report_data = generator.get_cash_flow()
        elif template.report_type == 'trial_balance':
            report_data = generator.get_trial_balance()
        elif template.report_type == 'accounts_receivable':
            report_data = generator.get_accounts_aging('receivable')
        elif template.report_type == 'accounts_payable':
            report_data = generator.get_accounts_aging('payable')

        report.report_data = report_data
        report.save()

        serializer = self.get_serializer(report)
        return Response(serializer.data)