import re
from django.db import IntegrityError
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from apps.workflow.services import WorkflowService
from .models import SurrenderMineralRight
from .serializers import SurrenderMineralRightSerializer


class SurrenderProcessingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SurrenderMineralRight.objects.all()
    serializer_class = SurrenderMineralRightSerializer

    def get_workflow(self, instance):
        return WorkflowService.get_workflow_for_instance(instance)

    # --- List pending applications ---
    @action(detail=False, methods=['get'])
    def pending(self, request):
        pending_apps = self.queryset.filter(status_id=1)
        serializer = self.get_serializer(pending_apps, many=True)
        return Response(serializer.data)

    # --- Get available actions ---
    @action(detail=True, methods=['get'])
    def available_actions(self, request, pk=None):
        instance = self.get_object()
        try:
            workflow = self.get_workflow(instance)
            current_stage = WorkflowService.get_current_stage(
                workflow,
                instance.surrender_mineral_right_id
            )
            actions = WorkflowService.get_available_actions(
                workflow,
                instance.surrender_mineral_right_id
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

    # --- Perform any action ---
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
        instance = self.get_object()
        action_id = request.data.get('action_id')
        comment = request.data.get('comment', '')
        performed_by = request.data.get('performed_by', 0)

        if not action_id:
            return Response(
                {'error': 'action_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            workflow = self.get_workflow(instance)
            result = WorkflowService.execute_action(
                workflow,
                instance.surrender_mineral_right_id,
                action_id,
                comment,
                performed_by
            )
            instance.status_id = result['new_stage_id']
            instance.save()

            new_current_stage = WorkflowService.get_current_stage(
                workflow,
                instance.surrender_mineral_right_id
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
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            error_msg = str(e)
            if 'duplicate key' in error_msg.lower():
                return Response(
                    {'error': 'A history entry already exists for this application.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            match = re.search(r'Key \(([^)]+)\)=', error_msg)
            if match:
                column = match.group(1)
                return Response(
                    {'error': f'Invalid {column}. The provided ID does not exist.'},
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

    # --- Generate map (surrender-specific) ---
    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'map_url': {'type': 'string', 'description': 'URL to generated map image'},
                    'comment': {'type': 'string', 'description': 'Optional comment'},
                    'performed_by': {'type': 'integer', 'description': 'User ID performing the action'}
                },
                'required': ['map_url']
            }
        }
    )
    @action(detail=True, methods=['post'])
    def generate_map(self, request, pk=None):
        """
        Generate licence map for surrender.
        This is a custom action that performs action_id=2 (Generate Map).
        """
        instance = self.get_object()
        map_url = request.data.get('map_url')
        comment = request.data.get('comment', '')
        performed_by = request.data.get('performed_by', 0)

        if not map_url:
            return Response(
                {'error': 'map_url is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            workflow = self.get_workflow(instance)
            result = WorkflowService.execute_action(
                workflow,
                instance.surrender_mineral_right_id,
                2,  # ActionId for "Generate Map"
                f"Map generated: {map_url}. {comment}",
                performed_by
            )
            instance.status_id = result['new_stage_id']
            instance.save()

            return Response({
                'message': 'Map generated successfully',
                'new_stage': {
                    'id': result['new_stage_id'],
                    'name': result['new_stage_name']
                },
                'history_id': result['history_id']
            })
        except DjangoValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'error': f'An unexpected error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # --- Upload certificate (surrender-specific) ---
    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'certificate_url': {'type': 'string', 'description': 'URL to signed certificate'},
                    'comment': {'type': 'string', 'description': 'Optional comment'},
                    'performed_by': {'type': 'integer', 'description': 'User ID performing the action'}
                },
                'required': ['certificate_url']
            }
        }
    )
    @action(detail=True, methods=['post'])
    def upload_certificate(self, request, pk=None):
        """
        Upload signed surrender certificate.
        This is a custom action that performs action_id=3 (Upload Certificate).
        """
        instance = self.get_object()
        certificate_url = request.data.get('certificate_url')
        comment = request.data.get('comment', '')
        performed_by = request.data.get('performed_by', 0)

        if not certificate_url:
            return Response(
                {'error': 'certificate_url is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            workflow = self.get_workflow(instance)
            result = WorkflowService.execute_action(
                workflow,
                instance.surrender_mineral_right_id,
                3,  # ActionId for "Upload Certificate"
                f"Certificate uploaded: {certificate_url}. {comment}",
                performed_by
            )
            instance.status_id = result['new_stage_id']
            instance.save()

            return Response({
                'message': 'Certificate uploaded successfully',
                'new_stage': {
                    'id': result['new_stage_id'],
                    'name': result['new_stage_name']
                },
                'history_id': result['history_id']
            })
        except DjangoValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'error': f'An unexpected error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # --- Submit certificate (surrender-specific) ---
    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'comment': {'type': 'string', 'description': 'Optional comment'},
                    'performed_by': {'type': 'integer', 'description': 'User ID performing the action'}
                }
            }
        }
    )
    @action(detail=True, methods=['post'])
    def submit_certificate(self, request, pk=None):
        """
        Submit certificate to applicant.
        This is a custom action that performs action_id=4 (Submit Certificate).
        """
        instance = self.get_object()
        comment = request.data.get('comment', '')
        performed_by = request.data.get('performed_by', 0)

        try:
            workflow = self.get_workflow(instance)
            result = WorkflowService.execute_action(
                workflow,
                instance.surrender_mineral_right_id,
                4,  # ActionId for "Submit Certificate"
                f"Certificate submitted to applicant. {comment}",
                performed_by
            )
            instance.status_id = result['new_stage_id']
            instance.save()

            return Response({
                'message': 'Certificate submitted to applicant successfully',
                'new_stage': {
                    'id': result['new_stage_id'],
                    'name': result['new_stage_name']
                },
                'history_id': result['history_id']
            })
        except DjangoValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'error': f'An unexpected error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # --- Logs ---
    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        instance = self.get_object()
        try:
            logs = WorkflowService.get_logs(instance.surrender_mineral_right_id)
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