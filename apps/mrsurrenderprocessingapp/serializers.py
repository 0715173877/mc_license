from rest_framework import serializers
from .models import SurrenderMineralRight
from apps.workflow.services import WorkflowService

class SurrenderMineralRightSerializer(serializers.ModelSerializer):
    geo_coordinate_for_remaining_area = serializers.JSONField(required=False, allow_null=True)
    geo_coordinates_for_surrender_area = serializers.JSONField(required=False, allow_null=True)
    current_stage_name = serializers.SerializerMethodField()

    class Meta:
        model = SurrenderMineralRight
        fields = '__all__'
        read_only_fields = ['surrender_mineral_right_id', 'record_created_date', 'record_updated_date']

    def get_current_stage_name(self, obj):
        from django.core.exceptions import ValidationError
        try:
            workflow = WorkflowService.get_workflow_for_instance(obj)
            stage = WorkflowService.get_current_stage(workflow, obj.surrender_mineral_right_id)
            return stage.stage_name if stage else None
        except ValidationError:
            return None