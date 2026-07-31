import re
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import DraftSuspension, SuspendMineralRight, SuspensionDocument
from .serializers import (
    DraftSuspensionSerializer,
    SuspendMineralRightSerializer,
    SuspendMineralRightCreateSerializer,
    SuspensionDocumentSerializer,
)

# ---------- Request serializers ----------
class SubmitDraftRequestSerializer(serializers.Serializer):
    draft_id = serializers.IntegerField(required=True)

class SubmitRequestSerializer(serializers.Serializer):
    pass


# ---------- Draft CRUD ----------
class DraftSuspensionViewSet(viewsets.ModelViewSet):
    queryset = DraftSuspension.objects.all()
    serializer_class = DraftSuspensionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user_id = self.request.query_params.get('user_id')
        licence_id = self.request.query_params.get('licence_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if licence_id:
            queryset = queryset.filter(licence_id=licence_id)
        return queryset

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError as e:
            return Response(
                {'error': f'Database integrity error: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'An unexpected error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except IntegrityError as e:
            return Response(
                {'error': f'Database integrity error: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'An unexpected error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except Exception as e:
            return Response(
                {'error': f'An unexpected error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ---------- Final Suspension ----------
class SuspendMineralRightViewSet(viewsets.ModelViewSet):
    queryset = SuspendMineralRight.objects.all()
    serializer_class = SuspendMineralRightSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return SuspendMineralRightCreateSerializer
        return SuspendMineralRightSerializer

    # ---------- 1. Direct creation ----------
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            suspension = serializer.save()
        except IntegrityError as e:
            error_msg = str(e)
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
        out_serializer = SuspendMineralRightSerializer(suspension)
        return Response(out_serializer.data, status=status.HTTP_201_CREATED)

    # ---------- 2. Submit an existing suspension ----------
    @extend_schema(
        request=SubmitRequestSerializer,
        responses={200: SuspendMineralRightSerializer}
    )
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        suspension = self.get_object()

        if suspension.status_id == 2:
            return Response(
                {'error': 'Suspension already submitted.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        required = ['licence_id', 'suspension_reason', 'suspension_duration', 'suspension_date']
        missing = [f for f in required if not getattr(suspension, f, None)]
        if missing:
            return Response(
                {'error': f'Missing required fields: {", ".join(missing)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        suspension.status_id = 2
        suspension.save()
        serializer = self.get_serializer(suspension)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ---------- 3. Submit from draft ----------
    @extend_schema(
        request=SubmitDraftRequestSerializer,
        responses={201: SuspendMineralRightSerializer}
    )
    @action(detail=False, methods=['post'])
    def submit_from_draft(self, request):
        draft_id = request.data.get('draft_id')
        if not draft_id:
            return Response(
                {'error': 'draft_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            draft = DraftSuspension.objects.get(pk=draft_id)
        except DraftSuspension.DoesNotExist:
            return Response(
                {'error': f'Draft with id {draft_id} not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        data = draft.data

        required = ['licence_id', 'suspension_reason', 'suspension_duration', 'suspension_date']
        missing = [f for f in required if f not in data]
        if missing:
            return Response(
                {'error': f'Missing fields in draft data: {", ".join(missing)}.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            suspension = SuspendMineralRight.objects.create(
                licence_id=data['licence_id'],
                suspension_reason=data['suspension_reason'],
                suspension_duration=data['suspension_duration'],
                suspension_date=data['suspension_date'],
                status_id=data.get('status_id', 1),
                application_date=data.get('application_date'),
                suspension_certificate_number=data.get('suspension_certificate_number'),
                suspension_end_date=data.get('suspension_end_date'),
                legal_entity_id=data.get('legal_entity_id'),
                record_created_by=data.get('record_created_by'),
                guid=data.get('guid'),
                licence_type_id=data.get('licence_type_id'),
                licence_status_id=data.get('licence_status_id'),
            )
        except IntegrityError as e:
            error_msg = str(e)
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

        # ---------- Move documents ----------
        try:
            documents = data.get('documents', [])
            for doc_data in documents:
                SuspensionDocument.objects.create(
                    suspend_mineral_right=suspension,
                    document_type=doc_data.get('document_type'),
                    document_url=doc_data.get('document_url'),
                    file_name=doc_data.get('file_name', ''),
                    record_created_by=data.get('record_created_by'),
                )
        except Exception as e:
            return Response(
                {'error': f'Failed to move documents: {str(e)}. Suspension was created but documents may be missing.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        draft.delete()
        serializer = self.get_serializer(suspension)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # ---------- (Optional) Validate documents ----------
    @action(detail=True, methods=['post'])
    def validate_documents(self, request, pk=None):
        try:
            suspension = self.get_object()
        except Exception:
            return Response(
                {'error': f'Suspension with id {pk} not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response({'message': 'Document validation successful (simulated).'})