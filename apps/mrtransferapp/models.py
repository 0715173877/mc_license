from django.db import models

# mrtransferapp/models.py
from django.db import models

class DraftTransfer(models.Model):
    draft_id = models.AutoField(primary_key=True, db_column='DraftId')
    user_id = models.BigIntegerField(db_column='UserId', blank=True, null=True)
    licence_id = models.BigIntegerField(db_column='LicenceId', blank=True, null=True)
    data = models.JSONField(db_column='Data', default=dict)   # Now holds everything, including documents
    current_step = models.IntegerField(db_column='CurrentStep', default=1)
    record_created_date = models.DateTimeField(db_column='RecordCreatedDate', auto_now_add=True)
    record_updated_date = models.DateTimeField(db_column='RecordUpdatedDate', auto_now=True)

    class Meta:
        managed = False
        db_table = '"mcmis"."Mr_DraftTransfer"'

class TransferMineralRight(models.Model):
    transfer_mineral_right_id = models.BigAutoField(primary_key=True, db_column='TransferMineralRightId')
    transferee_id = models.BigIntegerField(db_column='TransfereeId', blank=True, null=True)
    transferer_id = models.BigIntegerField(db_column='TransfererId', blank=True, null=True)
    licence_id = models.BigIntegerField(db_column='LicenceId', blank=True, null=True)
    transferred_share = models.DecimalField(max_digits=39, decimal_places=2, db_column='TransferredShare')
    transferee_type = models.CharField(max_length=255, db_column='TransfereeType', blank=True, null=True)
    status_id = models.IntegerField(db_column='StatusId', blank=True, null=True)
    effective_date = models.DateTimeField(db_column='EffectiveDate', blank=True, null=True)
    licence_status_id = models.BigIntegerField(db_column='LicenceStatusId', blank=True, null=True)
    guid = models.CharField(max_length=255, db_column='Guid', blank=True, null=True)
    record_created_by = models.BigIntegerField(db_column='RecordCreatedBy', blank=True, null=True)
    record_created_date = models.DateTimeField(db_column='RecordCreatedDate', auto_now_add=True, blank=True, null=True)
    record_updated_by = models.BigIntegerField(db_column='RecordUpdatedBy', blank=True, null=True)
    record_updated_date = models.DateTimeField(db_column='RecordUpdatedDate', auto_now=True, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"mcmis"."Mr_TransferMineralRght"'

class TransferDocument(models.Model):
    transfer_document_id = models.BigAutoField(primary_key=True, db_column='TransferDocumentId')
    transfer = models.ForeignKey(TransferMineralRight, on_delete=models.CASCADE, db_column='TransferMineralRightId')
    document_type = models.CharField(max_length=50, db_column='DocumentType')
    document_url = models.TextField(db_column='DocumentUrl')
    file_name = models.CharField(max_length=255, db_column='FileName', blank=True, null=True)
    record_created_by = models.BigIntegerField(db_column='RecordCreatedBy', blank=True, null=True)
    record_created_date = models.DateTimeField(db_column='RecordCreatedDate', auto_now_add=True)

    class Meta:
        managed = False
        db_table = '"mcmis"."Mr_TransferDocument"'