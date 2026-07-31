from rest_framework import serializers
from .models import DraftComplexShape, ComplexShapeDocument

class DraftComplexShapeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DraftComplexShape
        fields = '__all__'
        read_only_fields = ['draft_id', 'record_created_date', 'record_updated_date']

class ComplexShapeDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplexShapeDocument
        fields = '__all__'
        read_only_fields = ['complex_shape_document_id', 'record_created_date', 'record_updated_date']

class ComplexShapeDocumentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplexShapeDocument
        fields = [
            'licence_id', 'document_type', 'document_url', 'description',
            'status_id', 'record_created_by', 'guid'
        ]
        extra_kwargs = {
            'status_id': {'default': 1},
        }