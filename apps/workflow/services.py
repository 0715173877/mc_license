from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Workflow, Stage, Action, Transition, WorkflowHistory, WorkflowModelMapping

class WorkflowService:

    @staticmethod
    def get_workflow_for_instance(instance):
        model_name = instance.__class__.__name__
        try:
            mapping = WorkflowModelMapping.objects.get(model_name=model_name)
            return mapping.workflow
        except WorkflowModelMapping.DoesNotExist:
            raise ValidationError(f"No workflow mapping found for model '{model_name}'")

    @staticmethod
    def get_workflow_by_abbreviation(abbreviation):
        try:
            return Workflow.objects.get(abbreviation=abbreviation)
        except Workflow.DoesNotExist:
            raise ValidationError(f"No workflow found for abbreviation '{abbreviation}'")

    @staticmethod
    def get_current_stage(application_type, application_id):
        if isinstance(application_type, Workflow):
            workflow = application_type
        else:
            workflow = WorkflowService.get_workflow_by_abbreviation(application_type)

        # Get the latest history entry for this application
        latest = WorkflowHistory.objects.filter(
            application_id=application_id
        ).order_by('-performed_date').first()

        if latest:
            return latest.to_stage
        else:
            # No history yet – return the initial stage
            first_transition = Transition.objects.filter(
                workflow=workflow,
                status_id=1
            ).order_by('sequence_number').first()
            if not first_transition:
                raise ValidationError(f"No transitions found for workflow '{workflow.workflow_name}'")
            return first_transition.current_stage

    @staticmethod
    def get_available_actions(application_type, application_id):
        if isinstance(application_type, Workflow):
            workflow = application_type
        else:
            workflow = WorkflowService.get_workflow_by_abbreviation(application_type)

        current_stage = WorkflowService.get_current_stage(workflow, application_id)
        transitions = Transition.objects.filter(
            workflow=workflow,
            current_stage=current_stage,
            status_id=1
        ).select_related('action', 'next_stage')

        return [
            {
                'action_id': t.action.action_id,
                'action_name': t.action.action_name,
                'next_stage_id': t.next_stage.stage_id,
                'next_stage_name': t.next_stage.stage_name,
            }
            for t in transitions
        ]

    @staticmethod
    @transaction.atomic
    def execute_action(application_type, application_id, action_id, comment, performed_by):
        if isinstance(application_type, Workflow):
            workflow = application_type
        else:
            workflow = WorkflowService.get_workflow_by_abbreviation(application_type)

        current_stage = WorkflowService.get_current_stage(workflow, application_id)

        transition = Transition.objects.filter(
            workflow=workflow,
            current_stage=current_stage,
            action_id=action_id,
            status_id=1
        ).first()

        if not transition:
            raise ValidationError(
                f"Action {action_id} is not available from current stage '{current_stage.stage_name}'"
            )

        # Create history entry
        history = WorkflowHistory.objects.create(
            application_id=application_id,
            action=transition.action,
            from_stage=current_stage,
            to_stage=transition.next_stage,
            comment=comment,
            performed_by=performed_by,
        )

        return {
            'new_stage_id': transition.next_stage.stage_id,
            'new_stage_name': transition.next_stage.stage_name,
            'action_name': transition.action.action_name,
            'history_id': history.workflow_history_id,
        }

    @staticmethod
    def get_logs(application_id):
        return WorkflowHistory.objects.filter(
            application_id=application_id
        ).select_related('action', 'from_stage', 'to_stage').order_by('-performed_date')