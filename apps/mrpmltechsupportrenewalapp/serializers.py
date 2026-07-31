from rest_framework import serializers
from .models import DraftPmlTechSupportRenewal, PmlTechnicalSupport, PmlTechSupportDocument

class DraftPmlTechSupportRenewalSerializer(serializers.ModelSerializer):
    class Meta:
        model = DraftPmlTechSupportRenewal
        fields = '__all__'
        read_only_fields = ['draft_id', 'record_created_date', 'record_updated_date']

class PmlTechSupportDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PmlTechSupportDocument
        fields = '__all__'
        read_only_fields = ['pml_tech_support_document_id', 'record_created_date']

class PmlTechnicalSupportSerializer(serializers.ModelSerializer):
    documents = PmlTechSupportDocumentSerializer(source='pmltechsupportdocument_set', many=True, read_only=True)

    class Meta:
        model = PmlTechnicalSupport
        fields = '__all__'
        read_only_fields = [
            'pml_technical_support_id', 'record_created_date', 'record_updated_date'
        ]

class PmlTechnicalSupportCreateSerializer(serializers.ModelSerializer):
    documents = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        write_only=True
    )

    class Meta:
        model = PmlTechnicalSupport
        fields = [
            'licence_id', 'ts_type', 'ts_provider_category', 'legal_entity_id',
            'technical_support_certificate_number', 'issued_date', 'duration',
            'expiry_date', 'is_fresh_application', 'status_id', 'mineral_right_id',
            'record_created_by', 'guid', 'licence_status_id', 'documents'
        ]
        extra_kwargs = {
            'status_id': {'default': 1},
            'is_fresh_application': {'default': False},  # renewal => False
        }

    def create(self, validated_data):
        documents_data = validated_data.pop('documents', [])
        pml_ts = PmlTechnicalSupport.objects.create(**validated_data)
        for doc_data in documents_data:
            PmlTechSupportDocument.objects.create(
                pml_technical_support=pml_ts,
                document_type=doc_data.get('document_type'),
                document_url=doc_data.get('document_url'),
                file_name=doc_data.get('file_name', ''),
                record_created_by=validated_data.get('record_created_by')
            )
        return pml_ts