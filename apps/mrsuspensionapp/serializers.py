from rest_framework import serializers
from .models import DraftSuspension, SuspendMineralRight, SuspensionDocument

class DraftSuspensionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DraftSuspension
        fields = '__all__'
        read_only_fields = ['draft_id', 'record_created_date', 'record_updated_date']

class SuspensionDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuspensionDocument
        fields = '__all__'
        read_only_fields = ['suspension_document_id', 'record_created_date']

class SuspendMineralRightSerializer(serializers.ModelSerializer):
    documents = SuspensionDocumentSerializer(source='suspensiondocument_set', many=True, read_only=True)

    class Meta:
        model = SuspendMineralRight
        fields = '__all__'
        read_only_fields = [
            'suspend_mineral_right_id', 'record_created_date', 'record_updated_date'
        ]

class SuspendMineralRightCreateSerializer(serializers.ModelSerializer):
    documents = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        write_only=True
    )

    class Meta:
        model = SuspendMineralRight
        fields = [
            'licence_id', 'suspension_reason', 'suspension_duration',
            'status_id', 'application_date', 'suspension_certificate_number',
            'suspension_date', 'suspension_end_date', 'legal_entity_id',
            'record_created_by', 'guid', 'licence_type_id', 'licence_status_id',
            'documents'
        ]
        extra_kwargs = {
            'status_id': {'default': 1},
        }

    def create(self, validated_data):
        documents_data = validated_data.pop('documents', [])
        suspension = SuspendMineralRight.objects.create(**validated_data)
        for doc_data in documents_data:
            SuspensionDocument.objects.create(
                suspend_mineral_right=suspension,
                document_type=doc_data.get('document_type'),
                document_url=doc_data.get('document_url'),
                file_name=doc_data.get('file_name', ''),
                record_created_by=validated_data.get('record_created_by')
            )
        return suspension