from django.db import models

class DraftComplexShape(models.Model):
    draft_id = models.AutoField(primary_key=True, db_column='DraftId')
    user_id = models.BigIntegerField(db_column='UserId', blank=True, null=True)
    licence_id = models.BigIntegerField(db_column='LicenceId', blank=True, null=True)
    data = models.JSONField(db_column='Data', default=dict)
    current_step = models.IntegerField(db_column='CurrentStep', default=1)
    record_created_date = models.DateTimeField(db_column='RecordCreatedDate', auto_now_add=True)
    record_updated_date = models.DateTimeField(db_column='RecordUpdatedDate', auto_now=True)

    class Meta:
        managed = False
        db_table = '"mcmis"."Mr_DraftComplexShape"'

class ComplexShapeDocument(models.Model):
    complex_shape_document_id = models.BigAutoField(primary_key=True, db_column='ComplexShapeDocumentId')
    licence_id = models.BigIntegerField(db_column='LicenceId')
    document_type = models.CharField(max_length=60, db_column='DocumentType')
    document_url = models.TextField(db_column='DocumentUrl')
    description = models.CharField(max_length=500, db_column='Description', blank=True, null=True)
    status_id = models.IntegerField(db_column='StatusId', default=1)
    record_created_by = models.BigIntegerField(db_column='RecordCreatedBy', blank=True, null=True)
    record_created_date = models.DateTimeField(db_column='RecordCreatedDate', auto_now_add=True, blank=True, null=True)
    record_updated_by = models.BigIntegerField(db_column='RecordUpdatedBy', blank=True, null=True)
    record_updated_date = models.DateTimeField(db_column='RecordUpdatedDate', auto_now=True, blank=True, null=True)
    guid = models.CharField(max_length=255, db_column='Guid', blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"mcmis"."Mr_ComplexShapeDocument"'