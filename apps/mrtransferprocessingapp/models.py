from django.db import models

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