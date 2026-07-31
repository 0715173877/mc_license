from django.db import models

class PmlTechnicalSupport(models.Model):
    pml_technical_support_id = models.BigAutoField(primary_key=True, db_column='PmlTechnicalSupportId')
    licence_id = models.BigIntegerField(db_column='LicenceId', blank=True, null=True)
    ts_type = models.CharField(max_length=255, db_column='TsType', blank=True, null=True)
    ts_provider_category = models.CharField(max_length=255, db_column='TsProviderCategory', blank=True, null=True)
    legal_entity_id = models.BigIntegerField(db_column='LegalEntityId', blank=True, null=True)
    technical_support_certificate_number = models.CharField(max_length=255, db_column='TechnicalSupportCertificateNumber', blank=True, null=True)
    issued_date = models.DateTimeField(db_column='IssuedDate', blank=True, null=True)
    duration = models.IntegerField(db_column='Duration', blank=True, null=True)
    expiry_date = models.DateTimeField(db_column='ExpiryDate', blank=True, null=True)
    is_fresh_application = models.BooleanField(db_column='IsFreshApplication', blank=True, null=True)
    status_id = models.IntegerField(db_column='StatusId', blank=True, null=True)
    mineral_right_id = models.BigIntegerField(db_column='MineralRightId', blank=True, null=True)
    record_created_by = models.BigIntegerField(db_column='RecordCreatedBy', blank=True, null=True)
    record_created_date = models.DateTimeField(db_column='RecordCreatedDate', auto_now_add=True, blank=True, null=True)
    record_updated_by = models.BigIntegerField(db_column='RecordUpdatedBy', blank=True, null=True)
    record_updated_date = models.DateTimeField(db_column='RecordUpdatedDate', auto_now=True, blank=True, null=True)
    guid = models.CharField(max_length=255, db_column='Guid', blank=True, null=True)
    licence_status_id = models.BigIntegerField(db_column='LicenceStatusId', blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"mcmis"."Mr_PmlTechnicalSupport"'