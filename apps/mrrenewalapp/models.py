from django.db import models

class DraftRenewal(models.Model):
    draft_id = models.AutoField(primary_key=True, db_column='DraftId')
    user_id = models.BigIntegerField(db_column='UserId', blank=True, null=True)
    licence_id = models.BigIntegerField(db_column='LicenceId', blank=True, null=True)
    data = models.JSONField(db_column='Data', default=dict)
    current_step = models.IntegerField(db_column='CurrentStep', default=1)
    record_created_date = models.DateTimeField(db_column='RecordCreatedDate', auto_now_add=True)
    record_updated_date = models.DateTimeField(db_column='RecordUpdatedDate', auto_now=True)

    class Meta:
        managed = False
        db_table = '"mcmis"."Mr_DraftRenewal"'

class Renewal(models.Model):
    renewal_id = models.BigAutoField(primary_key=True, db_column='RenewalId')
    licence_id = models.BigIntegerField(db_column='LicenceId')
    is_same_shape = models.BooleanField(db_column='IsSameShape', default=True)
    new_coordinates = models.JSONField(db_column='NewCoordinates', blank=True, null=True)
    number_of_years = models.IntegerField(db_column='NumberOfYears')
    status_id = models.IntegerField(db_column='StatusId', default=1)
    legal_entity_id = models.BigIntegerField(db_column='LegalEntityId', blank=True, null=True)
    record_created_by = models.BigIntegerField(db_column='RecordCreatedBy', blank=True, null=True)
    record_created_date = models.DateTimeField(db_column='RecordCreatedDate', auto_now_add=True, blank=True, null=True)
    record_updated_by = models.BigIntegerField(db_column='RecordUpdatedBy', blank=True, null=True)
    record_updated_date = models.DateTimeField(db_column='RecordUpdatedDate', auto_now=True, blank=True, null=True)
    guid = models.CharField(max_length=255, db_column='Guid', blank=True, null=True)
    licence_status_id = models.BigIntegerField(db_column='LicenceStatusId', blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"mcmis"."Mr_Renewal"'

class RenewalDocument(models.Model):
    renewal_document_id = models.BigAutoField(primary_key=True, db_column='RenewalDocumentId')
    renewal = models.ForeignKey(
        Renewal,
        on_delete=models.CASCADE,
        db_column='RenewalId'
    )
    document_type = models.CharField(max_length=50, db_column='DocumentType')
    document_url = models.TextField(db_column='DocumentUrl')
    file_name = models.CharField(max_length=255, db_column='FileName', blank=True, null=True)
    record_created_by = models.BigIntegerField(db_column='RecordCreatedBy', blank=True, null=True)
    record_created_date = models.DateTimeField(db_column='RecordCreatedDate', auto_now_add=True)

    class Meta:
        managed = False
        db_table = '"mcmis"."Mr_RenewalDocument"'




