from django.db import models

class Workflow(models.Model):
    workflow_id = models.BigAutoField(primary_key=True, db_column='WorkflowId')
    workflow_name = models.CharField(max_length=255, db_column='WorkflowName')
    abbreviation = models.CharField(max_length=255, db_column='Abbreviation', blank=True, null=True, unique=True)
    description = models.TextField(db_column='Description', blank=True, null=True)
    status_id = models.BigIntegerField(db_column='StatusId', blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"mcmis"."Mr_Workflow"'

    def __str__(self):
        return f"{self.abbreviation}: {self.workflow_name}"

class Stage(models.Model):
    stage_id = models.BigAutoField(primary_key=True, db_column='StageId')
    stage_name = models.CharField(max_length=255, db_column='StageName')
    description = models.TextField(db_column='Description', blank=True, null=True)
    status_id = models.BigIntegerField(db_column='StatusId', blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"mcmis"."Mr_Stage"'

    def __str__(self):
        return self.stage_name

class Action(models.Model):
    action_id = models.BigAutoField(primary_key=True, db_column='ActionId')
    action_name = models.CharField(max_length=255, db_column='ActionName')
    description = models.TextField(db_column='Description', blank=True, null=True)
    status_id = models.BigIntegerField(db_column='StatusId', blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"mcmis"."Mr_Action"'

    def __str__(self):
        return self.action_name

class Transition(models.Model):
    transition_id = models.BigAutoField(primary_key=True, db_column='TransitionId')
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, db_column='WorkflowId')
    current_stage = models.ForeignKey(Stage, on_delete=models.CASCADE, db_column='CurrentStageId', related_name='transitions_from')
    next_stage = models.ForeignKey(Stage, on_delete=models.CASCADE, db_column='NextStageId', related_name='transitions_to')
    action = models.ForeignKey(Action, on_delete=models.CASCADE, db_column='ActionId')
    sequence_number = models.BigIntegerField(db_column='SequenceNumber', blank=True, null=True)
    status_id = models.BigIntegerField(db_column='StatusId', blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"mcmis"."Mr_Transition"'

class ApplicationHistory(models.Model):
    application_id = models.BigAutoField(primary_key=True, db_column='ApplicationId')
    note = models.CharField(max_length=255, db_column='Note', blank=True, null=True)
    decision = models.CharField(max_length=255, db_column='Decision', blank=True, null=True)
    from_stage = models.ForeignKey(Stage, on_delete=models.CASCADE, db_column='FromStageId', related_name='history_from', null=True)
    from_stage_name = models.CharField(max_length=255, db_column='FromStageName', blank=True, null=True)
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, db_column='StageId', related_name='history_to')
    to_stage_name = models.CharField(max_length=255, db_column='ToStageName', blank=True, null=True)
    record_created_by = models.BigIntegerField(db_column='RecordCreatedBy', blank=True, null=True)
    record_created_date = models.DateTimeField(db_column='RecordCreatedDate', auto_now_add=True, blank=True, null=True)
    record_updated_by = models.BigIntegerField(db_column='RecordUpdatedBy', blank=True, null=True)
    record_updated_date = models.DateTimeField(db_column='RecordUpdatedDate', auto_now=True, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"mcmis"."Mr_ApplicationHistory"'

class WorkflowModelMapping(models.Model):
    mapping_id = models.BigAutoField(primary_key=True, db_column='MappingId')
    model_name = models.CharField(max_length=100, db_column='ModelName', unique=True)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, db_column='WorkflowId')
    record_created_date = models.DateTimeField(db_column='RecordCreatedDate', auto_now_add=True)
    record_updated_date = models.DateTimeField(db_column='RecordUpdatedDate', auto_now=True)

    class Meta:
        managed = False
        db_table = '"mcmis"."Mr_WorkflowModelMapping"'


class WorkflowHistory(models.Model):
    workflow_history_id = models.BigAutoField(primary_key=True, db_column='WorkflowHistoryId')
    application_id = models.BigIntegerField(db_column='ApplicationId')
    action = models.ForeignKey(Action, on_delete=models.CASCADE, db_column='ActionId')
    from_stage = models.ForeignKey(Stage, on_delete=models.CASCADE, db_column='FromStageId', related_name='wf_history_from', null=True)
    to_stage = models.ForeignKey(Stage, on_delete=models.CASCADE, db_column='ToStageId', related_name='wf_history_to', null=True)
    comment = models.TextField(db_column='Comment', blank=True, null=True)
    performed_by = models.BigIntegerField(db_column='PerformedBy')
    performed_date = models.DateTimeField(db_column='PerformedDate', auto_now_add=True)

    class Meta:
        managed = False
        db_table = '"mcmis"."Mr_WorkflowHistory"'

        