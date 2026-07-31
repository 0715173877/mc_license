import json
from django.db import models

class SafeJSONFieldForText(models.TextField):
    """
    Stores JSON in a text column, and deserializes to Python dict/list.
    """
    def from_db_value(self, value, expression, connection):
        if value is None:
            return None
        if isinstance(value, (dict, list)):
            return value
        try:
            return json.loads(value)
        except (TypeError, ValueError):
            return value

    def to_python(self, value):
        if value is None:
            return None
        if isinstance(value, (dict, list)):
            return value
        try:
            return json.loads(value)
        except (TypeError, ValueError):
            return value

    def get_prep_value(self, value):
        if value is None:
            return None
        return json.dumps(value)

class DraftSurrender(models.Model):
    draft_id = models.AutoField(primary_key=True, db_column='DraftId')
    user_id = models.BigIntegerField(db_column='UserId', blank=True, null=True)
    licence_id = models.BigIntegerField(db_column='LicenceId', blank=True, null=True)
    data = models.JSONField(db_column='Data', default=dict)
    current_step = models.IntegerField(db_column='CurrentStep', default=1)
    record_created_date = models.DateTimeField(db_column='RecordCreatedDate', auto_now_add=True)
    record_updated_date = models.DateTimeField(db_column='RecordUpdatedDate', auto_now=True)

    class Meta:
        managed = False
        db_table = '"mcmis"."Mr_DraftSurrender"'

class SurrenderMineralRight(models.Model):
    surrender_mineral_right_id = models.BigAutoField(primary_key=True, db_column='SurrenderMineralRightId')
    licence_id = models.BigIntegerField(db_column='LicenceId', blank=True, null=True)
    reason_for_surrender = models.CharField(max_length=500, db_column='ReasonForSurrender', blank=True, null=True)
    effective_surrender_date = models.DateTimeField(db_column='EffectiveSurrenderDate', blank=True, null=True)
    shape_validation_result_id = models.IntegerField(db_column='ShapeValidationResultId', blank=True, null=True)
    status_id = models.IntegerField(db_column='StatusId', blank=True, null=True)
    record_created_by = models.BigIntegerField(db_column='RecordCreatedBy', blank=True, null=True)
    record_created_date = models.DateTimeField(db_column='RecordCreatedDate', auto_now_add=True, blank=True, null=True)
    record_updated_by = models.BigIntegerField(db_column='RecordUpdatedBy', blank=True, null=True)
    record_updated_date = models.DateTimeField(db_column='RecordUpdatedDate', auto_now=True, blank=True, null=True)
    legal_entity_id = models.BigIntegerField(db_column='LegalEntityId', blank=True, null=True)
    guid = models.CharField(max_length=255, db_column='Guid', blank=True, null=True)
    geo_coordinate_for_remaining_area = SafeJSONFieldForText(db_column='GeoCoordinateForRemainingArea', blank=True, null=True)
    geo_coordinates_for_surrender_area = SafeJSONFieldForText(db_column='GeoCoordinatesForSurrenderArea', blank=True, null=True)
    surrender_type = models.CharField(max_length=255, db_column='SurrenderType', blank=True, null=True)
    licence_status_id = models.BigIntegerField(db_column='LicenceStatusId', blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"mcmis"."Mr_SurrenderMineralRight"'