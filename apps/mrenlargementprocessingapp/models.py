import json
from django.db import models

class SafeJSONField(models.JSONField):
    """Custom JSONField that safely handles already-parsed JSON data."""
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        if isinstance(value, (dict, list)):
            return value
        try:
            return json.loads(value)
        except (TypeError, ValueError):
            return value

class EnlargeMineralRight(models.Model):
    enlarge_mineral_right_id = models.BigAutoField(primary_key=True, db_column='EnlargeMineralRightId')
    geocoordinate = SafeJSONField(db_column='Geocoordinate', blank=True, null=True)
    development_report = models.CharField(max_length=255, db_column='DevelopmentReport', blank=True, null=True)
    validation_result_id = models.BigIntegerField(db_column='ValidationResultId', blank=True, null=True)
    application_id = models.BigIntegerField(db_column='ApplicationId', blank=True, null=True)
    status_id = models.IntegerField(db_column='StatusId', blank=True, null=True)
    application_date = models.DateTimeField(db_column='ApplicationDate', blank=True, null=True)
    grant_date = models.DateTimeField(db_column='GrantDate', blank=True, null=True)
    legal_entity_id = models.BigIntegerField(db_column='LegalEntityId', blank=True, null=True)
    licence_id = models.BigIntegerField(db_column='LicenceId', blank=True, null=True)
    record_created_by = models.BigIntegerField(db_column='RecordCreatedBy', blank=True, null=True)
    record_created_date = models.DateTimeField(db_column='RecordCreatedDate', auto_now_add=True, blank=True, null=True)
    record_updated_by = models.BigIntegerField(db_column='RecordUpdatedBy', blank=True, null=True)
    record_updated_date = models.DateTimeField(db_column='RecordUpdatedDate', auto_now=True, blank=True, null=True)
    guid = models.CharField(max_length=255, db_column='Guid', blank=True, null=True)
    licence_status_id = models.BigIntegerField(db_column='LicenceStatusId', blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"mcmis"."Mr_EnlargeMineralRight"'