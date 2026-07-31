from rest_framework import serializers
from .models import DraftSurrender, SurrenderMineralRight

class DraftSurrenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = DraftSurrender
        fields = '__all__'
        read_only_fields = ['draft_id', 'record_created_date', 'record_updated_date']

class SurrenderMineralRightSerializer(serializers.ModelSerializer):
    geo_coordinate_for_remaining_area = serializers.JSONField(required=False, allow_null=True)
    geo_coordinates_for_surrender_area = serializers.JSONField(required=False, allow_null=True)

    class Meta:
        model = SurrenderMineralRight
        fields = '__all__'
        read_only_fields = [
            'surrender_mineral_right_id', 'record_created_date', 'record_updated_date'
        ]

class SurrenderMineralRightCreateSerializer(serializers.ModelSerializer):
    geo_coordinate_for_remaining_area = serializers.JSONField(required=False, allow_null=True)
    geo_coordinates_for_surrender_area = serializers.JSONField(required=False, allow_null=True)

    class Meta:
        model = SurrenderMineralRight
        fields = [
            'licence_id', 'reason_for_surrender', 'effective_surrender_date',
            'shape_validation_result_id', 'status_id', 'record_created_by',
            'legal_entity_id', 'guid', 'geo_coordinate_for_remaining_area',
            'geo_coordinates_for_surrender_area', 'surrender_type',
            'licence_status_id'
        ]
        extra_kwargs = {
            'status_id': {'default': 1},
        }