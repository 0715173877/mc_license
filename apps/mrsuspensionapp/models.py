from django.db import models

class DraftSuspension(models.Model):
    draft_id = models.AutoField(primary_key=True, db_column='DraftId')
    user_id = models.BigIntegerField(db_column='UserId', blank=True, null=True)
    licence_id = models.BigIntegerField(db_column='LicenceId', blank=True, null=True)
    data = models.JSONField(db_column='Data', default=dict)
    current_step = models.IntegerField(db_column='CurrentStep', default=1)
    record_created_date = models.DateTimeField(db_column='RecordCreatedDate', auto_now_add=True)
    record_updated_date = models.DateTimeField(db_column='RecordUpdatedDate', auto_now=True)

    class Meta:
        managed = False
        db_table = '"mcmis"."Mr_DraftSuspension"'

class SuspendMineralRight(models.Model):
    suspend_mineral_right_id = models.BigAutoField(primary_key=True, db_column='SuspendMineralRightId')
    licence_id = models.BigIntegerField(db_column='LicenceId', blank=True, null=True)
    suspension_reason = models.CharField(max_length=255, db_column='SuspensionReason', blank=True, null=True)
    suspension_duration = models.IntegerField(db_column='SuspensionDuration', blank=True, null=True)  # in months/weeks?
    status_id = models.BigIntegerField(db_column='StatusId', blank=True, null=True)
    application_date = models.DateTimeField(db_column='ApplicationDate', blank=True, null=True)
    suspension_certificate_number = models.CharField(max_length=50, db_column='SuspensionCertificateNumber', blank=True, null=True)
    suspension_date = models.DateTimeField(db_column='SuspensionDate', blank=True, null=True)
    suspension_end_date = models.DateTimeField(db_column='SuspensionEndDate', blank=True, null=True)
    legal_entity_id = models.BigIntegerField(db_column='LegalEntityId', blank=True, null=True)
    record_created_by = models.BigIntegerField(db_column='RecordCreatedBy', blank=True, null=True)
    record_created_date = models.DateTimeField(db_column='RecordCreatedDate', auto_now_add=True, blank=True, null=True)
    record_updated_by = models.BigIntegerField(db_column='RecordUpdatedBy', blank=True, null=True)
    record_updated_date = models.DateTimeField(db_column='RecordUpdatedDate', auto_now=True, blank=True, null=True)
    guid = models.CharField(max_length=255, db_column='Guid', blank=True, null=True)
    licence_type_id = models.BigIntegerField(db_column='LicenceTypeId', blank=True, null=True)
    licence_status_id = models.BigIntegerField(db_column='LicenceStatusId', blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"mcmis"."Mr_SuspendMineralRight"'

class SuspensionDocument(models.Model):
    suspension_document_id = models.BigAutoField(primary_key=True, db_column='SuspensionDocumentId')
    suspend_mineral_right = models.ForeignKey(
        SuspendMineralRight,
        on_delete=models.CASCADE,
        db_column='SuspendMineralRightId'
    )
    document_type = models.CharField(max_length=50, db_column='DocumentType')
    document_url = models.TextField(db_column='DocumentUrl')
    file_name = models.CharField(max_length=255, db_column='FileName', blank=True, null=True)
    record_created_by = models.BigIntegerField(db_column='RecordCreatedBy', blank=True, null=True)
    record_created_date = models.DateTimeField(db_column='RecordCreatedDate', auto_now_add=True)

    class Meta:
        managed = False
        db_table = '"mcmis"."Mr_SuspensionDocument"'