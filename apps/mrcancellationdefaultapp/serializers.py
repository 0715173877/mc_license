from rest_framework import serializers
from django.db import models  # <-- add this import
from .models import DraftCancellationDefault, CancellationSuspensionMineralRight, CancellationDefaultDocument

class DraftCancellationDefaultSerializer(serializers.ModelSerializer):
    class Meta:
        model = DraftCancellationDefault
        fields = '__all__'
        read_only_fields = ['draft_id', 'record_created_date', 'record_updated_date']

class CancellationDefaultDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CancellationDefaultDocument
        fields = '__all__'
        read_only_fields = ['cancellation_default_document_id', 'record_created_date']

class CancellationSuspensionMineralRightSerializer(serializers.ModelSerializer):
    documents = CancellationDefaultDocumentSerializer(
        source='cancellationdefaultdocument_set',
        many=True,
        read_only=True
    )

    class Meta:
        model = CancellationSuspensionMineralRight
        fields = '__all__'
        read_only_fields = [
            'record_created_date', 'record_updated_date'
        ]

class CancellationSuspensionMineralRightCreateSerializer(serializers.ModelSerializer):
    documents = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        write_only=True
    )

    class Meta:
        model = CancellationSuspensionMineralRight
        fields = [
            'legal_entity_id', 'cancellation_suspension_id', 'licence_id',
            'reason_for_suspension_or_cancellation', 'compliance_area',
            'comment', 'counter_comment', 'remedy_provided', 'remedy_sufficient',
            'deadline', 'userid_of_issuer_of_notice', 'is_approved_by_tc',
            'status_id', 'category', 'record_created_by', 'guid',
            'documents'
        ]
        extra_kwargs = {
            'status_id': {'default': 1},
            'cancellation_suspension_id': {'required': False, 'allow_null': True},
        }

    def create(self, validated_data):
        documents_data = validated_data.pop('documents', [])
        # Generate cancellation_suspension_id if not provided
        if 'cancellation_suspension_id' not in validated_data or validated_data['cancellation_suspension_id'] is None:
            max_id = CancellationSuspensionMineralRight.objects.aggregate(
                models.Max('cancellation_suspension_id')
            )['cancellation_suspension_id__max'] or 0
            validated_data['cancellation_suspension_id'] = max_id + 1

        cancellation = CancellationSuspensionMineralRight.objects.create(**validated_data)
        for doc_data in documents_data:
            CancellationDefaultDocument.objects.create(
                cancellation_suspension=cancellation,
                document_type=doc_data.get('document_type'),
                document_url=doc_data.get('document_url'),
                file_name=doc_data.get('file_name', ''),
                record_created_by=validated_data.get('record_created_by')
            )
        return cancellation