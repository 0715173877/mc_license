import re
from django.db import IntegrityError
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from apps.workflow.services import WorkflowService
from .models import EnlargeMineralRight
from .serializers import EnlargeMineralRightSerializer


class EnlargementProcessingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Back-office processing for Enlargement of Mineral Rights.
    Uses the workflow service to drive actions.
    """
    queryset = EnlargeMineralRight.objects.all()
    serializer_class = EnlargeMineralRightSerializer

    def get_workflow(self, instance):
        """Get the workflow for the given instance via the service."""
        return WorkflowService.get_workflow_for_instance(instance)

    # --- List pending applications ---
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """List all applications with status_id = 1 (Pending)."""
        pending_apps = self.queryset.filter(status_id=1)
        serializer = self.get_serializer(pending_apps, many=True)
        return Response(serializer.data)

    # --- Get available actions ---
    @action(detail=True, methods=['get'])
    def available_actions(self, request, pk=None):
        """
        Returns the current stage and available actions for the application.
        """
        instance = self.get_object()
        try:
            workflow = self.get_workflow(instance)
            current_stage = WorkflowService.get_current_stage(
                workflow,
                instance.enlarge_mineral_right_id
            )
            actions = WorkflowService.get_available_actions(
                workflow,
                instance.enlarge_mineral_right_id
            )
            return Response({
                'current_stage': {
                    'id': current_stage.stage_id,
                    'name': current_stage.stage_name
                },
                'available_actions': actions
            })
        except DjangoValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'error': f'An unexpected error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # --- Perform an action ---
    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'action_id': {'type': 'integer', 'description': 'ID of the action to perform'},
                    'comment': {'type': 'string', 'description': 'Optional comment'},
                    'performed_by': {'type': 'integer', 'description': 'User ID performing the action'}
                },
                'required': ['action_id']
            }
        },
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'new_stage': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'name': {'type': 'string'}
                        }
                    },
                    'history_id': {'type': 'integer'}
                }
            }
        }
    )
    @action(detail=True, methods=['post'])
    def perform_action(self, request, pk=None):
        """
        Executes the given action on the application.
        Expects: action_id (required), comment (optional), performed_by (optional).
        """
        instance = self.get_object()

        # Extract data
        action_id = request.data.get('action_id')
        comment = request.data.get('comment', '')
        performed_by = request.data.get('performed_by', 0)  # default to system user

        if not action_id:
            return Response(
                {'error': 'action_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            workflow = self.get_workflow(instance)
            result = WorkflowService.execute_action(
                workflow,
                instance.enlarge_mineral_right_id,
                action_id,
                comment,
                performed_by
            )

            # Update the application's status_id to the new stage ID
            instance.status_id = result['new_stage_id']
            instance.save()

            # Get the new current stage for response
            new_current_stage = WorkflowService.get_current_stage(
                workflow,
                instance.enlarge_mineral_right_id
            )

            return Response({
                'message': f"Action '{result['action_name']}' performed successfully",
                'new_stage': {
                    'id': new_current_stage.stage_id,
                    'name': new_current_stage.stage_name
                },
                'history_id': result['history_id']
            })

        except DjangoValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except IntegrityError as e:
            error_msg = str(e)
            # Try to extract meaningful info
            if 'duplicate key' in error_msg.lower():
                return Response(
                    {'error': 'A history entry already exists for this application. Please contact support.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Foreign key violations
            match = re.search(r'Key \(([^)]+)\)=', error_msg)
            if match:
                column = match.group(1)
                return Response(
                    {'error': f'Invalid {column}. The provided ID does not exist in the related table.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                {'error': f'Database integrity error: {error_msg}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'An unexpected error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # --- Get workflow logs ---
    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """
        Returns the workflow history for the application.
        """
        instance = self.get_object()
        try:
            logs = WorkflowService.get_logs(instance.enlarge_mineral_right_id)
            data = [
                {
                    'from_stage': log.from_stage.stage_name if log.from_stage else None,
                    'to_stage': log.to_stage.stage_name if log.to_stage else None,
                    'action': log.action.action_name if log.action else None,
                    'comment': log.comment,
                    'performed_by': log.performed_by,
                    'date': log.performed_date,
                }
                for log in logs
            ]
            return Response(data)
        except Exception as e:
            return Response(
                {'error': f'An unexpected error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )