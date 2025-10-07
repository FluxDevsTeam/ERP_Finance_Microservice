from rest_framework import serializers
from .models import JournalEntry, JournalLine
from apps.accounts.serializers import AccountSerializer


class JournalLineSerializer(serializers.ModelSerializer):
    account_details = AccountSerializer(source='account', read_only=True)

    class Meta:
        model = JournalLine
        fields = '__all__'
        read_only_fields = ('tenant', 'branch')


class JournalEntrySerializer(serializers.ModelSerializer):
    lines = JournalLineSerializer(source='journalline_set', many=True)
    
    class Meta:
        model = JournalEntry
        fields = '__all__'
        read_only_fields = ('total_amount', 'tenant', 'branch', 'created_by', 'updated_by',
                          'created_at', 'updated_at')

    def create(self, validated_data):
        lines_data = validated_data.pop('journalline_set')
        journal_entry = JournalEntry.objects.create(**validated_data)
        
        total_amount = 0
        for line_data in lines_data:
            line_data['tenant'] = journal_entry.tenant
            line_data['branch'] = journal_entry.branch
            JournalLine.objects.create(journal_entry=journal_entry, **line_data)
            if line_data['type'] == 'debit':
                total_amount += line_data['amount']
        
        journal_entry.total_amount = total_amount
        journal_entry.save()
        return journal_entry

    def update(self, instance, validated_data):
        if instance.status != 'draft':
            raise serializers.ValidationError("Only draft entries can be modified")
        
        lines_data = validated_data.pop('journalline_set')
        JournalLine.objects.filter(journal_entry=instance).delete()
        
        total_amount = 0
        for line_data in lines_data:
            line_data['tenant'] = instance.tenant
            line_data['branch'] = instance.branch
            JournalLine.objects.create(journal_entry=instance, **line_data)
            if line_data['type'] == 'debit':
                total_amount += line_data['amount']
        
        instance.total_amount = total_amount
        return super().update(instance, validated_data)