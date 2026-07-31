from rest_framework import serializers
from .models import TransferMineralRight
from apps.workflow.services import WorkflowService

class TransferMineralRightSerializer(serializers.ModelSerializer):
    current_stage_name = serializers.SerializerMethodField()

    class Meta:
        model = TransferMineralRight
        fields = '__all__'
        read_only_fields = ['transfer_mineral_right_id', 'record_created_date', 'record_updated_date']

    def get_current_stage_name(self, obj):
        from django.core.exceptions import ValidationError
        try:
            workflow = WorkflowService.get_workflow_for_instance(obj)
            stage = WorkflowService.get_current_stage(workflow, obj.transfer_mineral_right_id)
            return stage.stage_name if stage else None
        except ValidationError:
            return None