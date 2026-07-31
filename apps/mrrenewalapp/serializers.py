from rest_framework import serializers
from .models import DraftRenewal, Renewal, RenewalDocument

class DraftRenewalSerializer(serializers.ModelSerializer):
    class Meta:
        model = DraftRenewal
        fields = '__all__'
        read_only_fields = ['draft_id', 'record_created_date', 'record_updated_date']

class RenewalDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RenewalDocument
        fields = '__all__'
        read_only_fields = ['renewal_document_id', 'record_created_date']

class RenewalSerializer(serializers.ModelSerializer):
    documents = RenewalDocumentSerializer(source='renewaldocument_set', many=True, read_only=True)

    class Meta:
        model = Renewal
        fields = '__all__'
        read_only_fields = [
            'renewal_id', 'record_created_date', 'record_updated_date'
        ]

class RenewalCreateSerializer(serializers.ModelSerializer):
    documents = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        write_only=True
    )

    class Meta:
        model = Renewal
        fields = [
            'licence_id', 'is_same_shape', 'new_coordinates', 'number_of_years',
            'status_id', 'legal_entity_id', 'record_created_by', 'guid',
            'licence_status_id', 'documents'
        ]
        extra_kwargs = {
            'status_id': {'default': 1},
            'is_same_shape': {'default': True},
        }

    def create(self, validated_data):
        documents_data = validated_data.pop('documents', [])
        renewal = Renewal.objects.create(**validated_data)
        for doc_data in documents_data:
            RenewalDocument.objects.create(
                renewal=renewal,
                document_type=doc_data.get('document_type'),
                document_url=doc_data.get('document_url'),
                file_name=doc_data.get('file_name', ''),
                record_created_by=validated_data.get('record_created_by')
            )
        return renewal