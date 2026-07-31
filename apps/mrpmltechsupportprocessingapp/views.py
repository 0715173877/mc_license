import re
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from apps.workflow.models import Stage, Transition, WorkflowHistory, WorkflowModelMapping
from .models import PmlTechnicalSupport
from .serializers import PmlTechnicalSupportSerializer


class PmlTechSupportProcessingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PmlTechnicalSupport.objects.all()
    serializer_class = PmlTechnicalSupportSerializer

    def get_workflow_for_instance(self, instance):
        """Get workflow from mapping based on model name."""
        model_name = instance.__class__.__name__
        try:
            mapping = WorkflowModelMapping.objects.get(model_name=model_name)
            return mapping.workflow
        except WorkflowModelMapping.DoesNotExist:
            raise ValidationError(f"No workflow mapping for {model_name}")

    @action(detail=False, methods=['get'])
    def pending(self, request):
        pending_apps = self.queryset.filter(status_id=1)
        serializer = self.get_serializer(pending_apps, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def available_actions(self, request, pk=None):
        instance = self.get_object()
        try:
            workflow = self.get_workflow_for_instance(instance)
            current_stage = Stage.objects.get(stage_id=instance.status_id)
            transitions = Transition.objects.filter(
                workflow=workflow,
                current_stage=current_stage,
                status_id=1
            ).select_related('action', 'next_stage')

            actions = [
                {
                    'action_id': t.action.action_id,
                    'action_name': t.action.action_name,
                    'next_stage_id': t.next_stage.stage_id,
                    'next_stage_name': t.next_stage.stage_name,
                }
                for t in transitions
            ]

            return Response({
                'current_stage': {
                    'id': current_stage.stage_id,
                    'name': current_stage.stage_name
                },
                'available_actions': actions
            })
        except Stage.DoesNotExist:
            return Response({'error': f'Invalid stage ID {instance.status_id}'}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    def _execute_action(self, instance, action_id, comment, performed_by):
        """Execute an action using status_id as the source of truth."""
        try:
            workflow = self.get_workflow_for_instance(instance)
            current_stage = Stage.objects.get(stage_id=instance.status_id)

            transition = Transition.objects.filter(
                workflow=workflow,
                current_stage=current_stage,
                action_id=action_id,
                status_id=1
            ).first()

            if not transition:
                return Response(
                    {'error': f'Action {action_id} not available from current stage "{current_stage.stage_name}".'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create history entry
            history = WorkflowHistory.objects.create(
                application_id=instance.pml_technical_support_id,
                action=transition.action,
                from_stage=current_stage,
                to_stage=transition.next_stage,
                comment=comment,
                performed_by=performed_by,
            )

            # Update application status_id to the next stage
            instance.status_id = transition.next_stage.stage_id
            instance.save()

            new_stage = transition.next_stage

            return Response({
                'message': f"Action '{transition.action.action_name}' performed successfully",
                'new_stage': {
                    'id': new_stage.stage_id,
                    'name': new_stage.stage_name
                },
                'history_id': history.workflow_history_id
            })
        except Stage.DoesNotExist:
            return Response({'error': f'Invalid stage ID {instance.status_id}'}, status=400)
        except IntegrityError as e:
            if 'duplicate key' in str(e):
                return Response({'error': 'History entry already exists'}, status=400)
            return Response({'error': f'Database error: {str(e)}'}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

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
        }
    )
    @action(detail=True, methods=['post'])
    def perform_action(self, request, pk=None):
        instance = self.get_object()
        action_id = request.data.get('action_id')
        comment = request.data.get('comment', '')
        performed_by = request.data.get('performed_by', 0)

        if not action_id:
            return Response({'error': 'action_id required'}, status=400)

        return self._execute_action(instance, action_id, comment, performed_by)

    @action(detail=True, methods=['post'])
    def hq_recommendation(self, request, pk=None):
        instance = self.get_object()
        recommendation = request.data.get('recommendation')
        comment = request.data.get('comment', '')
        performed_by = request.data.get('performed_by', 0)
        if not recommendation:
            return Response({'error': 'recommendation required'}, status=400)
        return self._execute_action(instance, 32, f"HQ Recommendation: {recommendation}. {comment}", performed_by)

    @action(detail=True, methods=['post'])
    def legal_review(self, request, pk=None):
        instance = self.get_object()
        legal_status = request.data.get('legal_status')
        comment = request.data.get('comment', '')
        performed_by = request.data.get('performed_by', 0)
        if not legal_status:
            return Response({'error': 'legal_status required'}, status=400)
        return self._execute_action(instance, 33, f"Legal Status: {legal_status}. {comment}", performed_by)

    @action(detail=True, methods=['post'])
    def tc_opinion(self, request, pk=None):
        instance = self.get_object()
        tc_opinion = request.data.get('tc_opinion')
        comment = request.data.get('comment', '')
        performed_by = request.data.get('performed_by', 0)
        if not tc_opinion:
            return Response({'error': 'tc_opinion required'}, status=400)
        return self._execute_action(instance, 34, f"TC Opinion: {tc_opinion}. {comment}", performed_by)

    @action(detail=True, methods=['post'])
    def issue_certificate(self, request, pk=None):
        instance = self.get_object()
        certificate_url = request.data.get('certificate_url')
        comment = request.data.get('comment', '')
        performed_by = request.data.get('performed_by', 0)
        if not certificate_url:
            return Response({'error': 'certificate_url required'}, status=400)
        return self._execute_action(instance, 35, f"Certificate issued: {certificate_url}. {comment}", performed_by)

    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        instance = self.get_object()
        logs = WorkflowHistory.objects.filter(
            application_id=instance.pml_technical_support_id
        ).select_related('action', 'from_stage', 'to_stage').order_by('-performed_date')
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