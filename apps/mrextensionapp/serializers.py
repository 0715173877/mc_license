from rest_framework import serializers
from .models import DraftExtension, ExtensionToCommenceMining

class DraftExtensionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DraftExtension
        fields = '__all__'
        read_only_fields = ['draft_id', 'record_created_date', 'record_updated_date']

class ExtensionToCommenceMiningSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtensionToCommenceMining
        fields = '__all__'
        read_only_fields = [
            'extension_to_commence_mining_id', 'record_created_date', 'record_updated_date'
        ]

class ExtensionToCommenceMiningCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtensionToCommenceMining
        fields = [
            'licence_id', 'extension_reason', 'extension_duration',
            'status_id', 'application_date', 'issued_date',
            'legal_entity_id', 'record_created_by', 'extension_certificate_number',
            'expiry_date', 'licence_status_id'
        ]
        extra_kwargs = {
            'status_id': {'default': 1},
        }