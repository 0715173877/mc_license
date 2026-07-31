from django.db import models

class DraftPmlTechSupportRenewal(models.Model):
    draft_id = models.AutoField(primary_key=True, db_column='DraftId')
    user_id = models.BigIntegerField(db_column='UserId', blank=True, null=True)
    licence_id = models.BigIntegerField(db_column='LicenceId', blank=True, null=True)
    data = models.JSONField(db_column='Data', default=dict)
    current_step = models.IntegerField(db_column='CurrentStep', default=1)
    record_created_date = models.DateTimeField(db_column='RecordCreatedDate', auto_now_add=True)
    record_updated_date = models.DateTimeField(db_column='RecordUpdatedDate', auto_now=True)

    class Meta:
        managed = False
        db_table = '"mcmis"."Mr_DraftPmlTechSupportRenewal"'

class PmlTechnicalSupport(models.Model):
    # Same as in the other app – we define it here again (managed=False).
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

class PmlTechSupportDocument(models.Model):
    pml_tech_support_document_id = models.BigAutoField(primary_key=True, db_column='PmlTechSupportDocumentId')
    pml_technical_support = models.ForeignKey(
        PmlTechnicalSupport,
        on_delete=models.CASCADE,
        db_column='PmlTechnicalSupportId'
    )
    document_type = models.CharField(max_length=50, db_column='DocumentType')
    document_url = models.TextField(db_column='DocumentUrl')
    file_name = models.CharField(max_length=255, db_column='FileName', blank=True, null=True)
    record_created_by = models.BigIntegerField(db_column='RecordCreatedBy', blank=True, null=True)
    record_created_date = models.DateTimeField(db_column='RecordCreatedDate', auto_now_add=True)

    class Meta:
        managed = False
        db_table = '"mcmis"."Mr_PmlTechSupportDocument"'