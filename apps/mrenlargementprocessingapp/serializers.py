from rest_framework import serializers
from .models import EnlargeMineralRight
from apps.workflow.services import WorkflowService

class EnlargeMineralRightSerializer(serializers.ModelSerializer):
    geocoordinate = serializers.JSONField(required=False, allow_null=True)
    current_stage_name = serializers.SerializerMethodField()

    class Meta:
        model = EnlargeMineralRight
        fields = '__all__'
        read_only_fields = ['enlarge_mineral_right_id', 'record_created_date', 'record_updated_date']

    def get_current_stage_name(self, obj):
        from django.core.exceptions import ValidationError
        try:
            workflow = WorkflowService.get_workflow_for_instance(obj)
            stage = WorkflowService.get_current_stage(workflow, obj.enlarge_mineral_right_id)
            return stage.stage_name if stage else None
        except ValidationError:
            return None