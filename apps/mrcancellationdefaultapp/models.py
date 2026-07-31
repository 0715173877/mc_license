from django.db import models

class DraftCancellationDefault(models.Model):
    draft_id = models.AutoField(primary_key=True, db_column='DraftId')
    user_id = models.BigIntegerField(db_column='UserId', blank=True, null=True)
    licence_id = models.BigIntegerField(db_column='LicenceId', blank=True, null=True)
    data = models.JSONField(db_column='Data', default=dict)
    current_step = models.IntegerField(db_column='CurrentStep', default=1)
    record_created_date = models.DateTimeField(db_column='RecordCreatedDate', auto_now_add=True)
    record_updated_date = models.DateTimeField(db_column='RecordUpdatedDate', auto_now=True)

    class Meta:
        managed = False
        db_table = '"mcmis"."Mr_DraftCancellationDefault"'

class CancellationSuspensionMineralRight(models.Model):
    legal_entity_id = models.BigIntegerField(primary_key=True, db_column='LegalEntityId')
    cancellation_suspension_id = models.BigIntegerField(db_column='CancellationSuspensionId', unique=True)
    licence_id = models.BigIntegerField(db_column='LicenceId', blank=True, null=True)
    reason_for_suspension_or_cancellation = models.TextField(db_column='ReasonforSuspensionOrCancellation', blank=True, null=True)
    compliance_area = models.CharField(max_length=255, db_column='ComplianceArea', blank=True, null=True)
    comment = models.TextField(db_column='Comment', blank=True, null=True)
    counter_comment = models.TextField(db_column='CounterComment', blank=True, null=True)
    remedy_provided = models.CharField(max_length=255, db_column='RemedyProvided', blank=True, null=True)
    remedy_sufficient = models.BooleanField(db_column='RemedySufficient', blank=True, null=True)
    deadline = models.DateTimeField(db_column='Deadline', blank=True, null=True)
    userid_of_issuer_of_notice = models.BigIntegerField(db_column='UseridOfIssuerOfNotice', blank=True, null=True)
    is_approved_by_tc = models.BooleanField(db_column='IsApprovedbyTC', blank=True, null=True)
    status_id = models.IntegerField(db_column='StatusId', blank=True, null=True)
    category = models.BigIntegerField(db_column='Category', blank=True, null=True)
    record_created_by = models.BigIntegerField(db_column='RecordCreatedBy', blank=True, null=True)
    record_created_date = models.DateTimeField(db_column='RecordCreatedDate', auto_now_add=True, blank=True, null=True)
    record_updated_by = models.BigIntegerField(db_column='RecordUpdatedBy', blank=True, null=True)
    record_updated_date = models.DateTimeField(db_column='RecordUpdatedDate', auto_now=True, blank=True, null=True)
    guid = models.CharField(max_length=255, db_column='Guid', blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"mcmis"."Mr_CancellationSuspensionMineralRight"'

class CancellationDefaultDocument(models.Model):
    cancellation_default_document_id = models.BigAutoField(primary_key=True, db_column='CancellationDefaultDocumentId')
    cancellation_suspension = models.ForeignKey(
        CancellationSuspensionMineralRight,
        on_delete=models.CASCADE,
        db_column='CancellationSuspensionId',
        to_field='cancellation_suspension_id'
    )
    document_type = models.CharField(max_length=50, db_column='DocumentType')
    document_url = models.TextField(db_column='DocumentUrl')
    file_name = models.CharField(max_length=255, db_column='FileName', blank=True, null=True)
    record_created_by = models.BigIntegerField(db_column='RecordCreatedBy', blank=True, null=True)
    record_created_date = models.DateTimeField(db_column='RecordCreatedDate', auto_now_add=True)

    class Meta:
        managed = False
        db_table = '"mcmis"."Mr_CancellationDefaultDocument"'