from rest_framework import serializers
from .models import DraftEnlargement, EnlargeMineralRight

class DraftEnlargementSerializer(serializers.ModelSerializer):
    class Meta:
        model = DraftEnlargement
        fields = '__all__'
        read_only_fields = ['draft_id', 'record_created_date', 'record_updated_date']

class EnlargeMineralRightSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnlargeMineralRight
        fields = '__all__'
        read_only_fields = [
            'enlarge_mineral_right_id', 'record_created_date', 'record_updated_date'
        ]

class EnlargeMineralRightCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnlargeMineralRight
        fields = [
            'licence_id', 'geocoordinate', 'development_report',
            'validation_result_id', 'application_id', 'status_id',
            'application_date', 'grant_date', 'legal_entity_id',
            'record_created_by', 'guid', 'licence_status_id'
        ]
        extra_kwargs = {
            'status_id': {'default': 1},
        }