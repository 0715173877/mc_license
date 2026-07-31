from rest_framework import serializers
from .models import PmlTechnicalSupport
from apps.workflow.models import Stage

class PmlTechnicalSupportSerializer(serializers.ModelSerializer):
    current_stage_name = serializers.SerializerMethodField()

    class Meta:
        model = PmlTechnicalSupport
        fields = '__all__'
        read_only_fields = ['pml_technical_support_id', 'record_created_date', 'record_updated_date']

    def get_current_stage_name(self, obj):
        try:
            stage = Stage.objects.get(stage_id=obj.status_id)
            return stage.stage_name
        except Stage.DoesNotExist:
            return None