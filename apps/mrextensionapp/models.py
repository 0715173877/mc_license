from django.db import models

class DraftExtension(models.Model):
    draft_id = models.AutoField(primary_key=True, db_column='DraftId')
    user_id = models.BigIntegerField(db_column='UserId', blank=True, null=True)
    licence_id = models.BigIntegerField(db_column='LicenceId', blank=True, null=True)
    data = models.JSONField(db_column='Data', default=dict)
    current_step = models.IntegerField(db_column='CurrentStep', default=1)
    record_created_date = models.DateTimeField(db_column='RecordCreatedDate', auto_now_add=True)
    record_updated_date = models.DateTimeField(db_column='RecordUpdatedDate', auto_now=True)

    class Meta:
        managed = False
        db_table = '"mcmis"."Mr_DraftExtension"'

class ExtensionToCommenceMining(models.Model):
    extension_to_commence_mining_id = models.BigAutoField(primary_key=True, db_column='ExtensionToCommenceMiningId')
    licence_id = models.BigIntegerField(db_column='LicenceId', blank=True, null=True)
    extension_reason = models.CharField(max_length=255, db_column='ExtensionReason', blank=True, null=True)
    status_id = models.IntegerField(db_column='StatusId', blank=True, null=True)
    application_date = models.DateTimeField(db_column='ApplicationDate', blank=True, null=True)
    extension_duration = models.BigIntegerField(db_column='ExtensionDuration', blank=True, null=True)
    issued_date = models.DateTimeField(db_column='IssuedDate', blank=True, null=True)
    legal_entity_id = models.BigIntegerField(db_column='LegalEntityId', blank=True, null=True)
    record_created_by = models.BigIntegerField(db_column='RecordCreatedBy', blank=True, null=True)
    record_created_date = models.DateTimeField(db_column='RecordCreatedDate', auto_now_add=True, blank=True, null=True)
    record_updated_by = models.BigIntegerField(db_column='RecordUpdatedBy', blank=True, null=True)
    record_updated_date = models.DateTimeField(db_column='RecordUpdatedDate', auto_now=True, blank=True, null=True)
    extension_certificate_number = models.CharField(max_length=50, db_column='ExtensionCertificateNumber', blank=True, null=True)
    expiry_date = models.DateTimeField(db_column='ExpiryDate', blank=True, null=True)
    licence_status_id = models.BigIntegerField(db_column='LicenceStatusId', blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"mcmis"."Mr_ExtensionToCommenceMining"'