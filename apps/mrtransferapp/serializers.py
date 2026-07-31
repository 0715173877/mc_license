# apps/mrtransferapp/serializers.py
from rest_framework import serializers
from .models import DraftTransfer, TransferMineralRight, TransferDocument

# --- Existing serializers ---
class DraftTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = DraftTransfer
        fields = '__all__'
        read_only_fields = ['draft_id', 'record_created_date', 'record_updated_date']

class TransferDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferDocument
        fields = '__all__'
        read_only_fields = ['transfer_document_id', 'record_created_date']

class TransferMineralRightSerializer(serializers.ModelSerializer):
    documents = TransferDocumentSerializer(source='transferdocument_set', many=True, read_only=True)

    class Meta:
        model = TransferMineralRight
        fields = '__all__'
        read_only_fields = [
            'transfer_mineral_right_id', 'guid', 'record_created_date', 'record_updated_date'
        ]

# --- Create serializer for direct creation (with nested documents) ---
class TransferDocumentCreateSerializer(serializers.Serializer):
    document_type = serializers.CharField(max_length=50)
    document_url = serializers.URLField()
    file_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    record_created_by = serializers.IntegerField(required=False, allow_null=True)

class TransferMineralRightCreateSerializer(serializers.ModelSerializer):
    documents = TransferDocumentCreateSerializer(many=True, required=False)

    class Meta:
        model = TransferMineralRight
        fields = [
            'transferee_id', 'transferer_id', 'licence_id',
            'transferred_share', 'transferee_type', 'status_id',
            'effective_date', 'licence_status_id', 'guid',
            'record_created_by', 'documents'
        ]
        extra_kwargs = {
            'status_id': {'default': 1},  # default to draft
        }

    def create(self, validated_data):
        docs_data = validated_data.pop('documents', [])
        transfer = TransferMineralRight.objects.create(**validated_data)
        for doc_data in docs_data:
            TransferDocument.objects.create(transfer=transfer, **doc_data)
        return transfer