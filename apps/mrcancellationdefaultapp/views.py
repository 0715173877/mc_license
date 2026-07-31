import re
from django.db import IntegrityError, models
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import DraftCancellationDefault, CancellationSuspensionMineralRight, CancellationDefaultDocument
from .serializers import (
    DraftCancellationDefaultSerializer,
    CancellationSuspensionMineralRightSerializer,
    CancellationSuspensionMineralRightCreateSerializer,
    CancellationDefaultDocumentSerializer,
)

# ---------- Request serializers ----------
class SubmitDraftRequestSerializer(serializers.Serializer):
    draft_id = serializers.IntegerField(required=True)

class SubmitRequestSerializer(serializers.Serializer):
    pass


# ---------- Draft CRUD ----------
class DraftCancellationDefaultViewSet(viewsets.ModelViewSet):
    queryset = DraftCancellationDefault.objects.all()
    serializer_class = DraftCancellationDefaultSerializer

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


# ---------- Final Cancellation Default ----------
class CancellationSuspensionMineralRightViewSet(viewsets.ModelViewSet):
    queryset = CancellationSuspensionMineralRight.objects.all()
    serializer_class = CancellationSuspensionMineralRightSerializer
    lookup_field = 'legal_entity_id'   # because primary key is legal_entity_id

    def get_serializer_class(self):
        if self.action == 'create':
            return CancellationSuspensionMineralRightCreateSerializer
        return CancellationSuspensionMineralRightSerializer

    # ---------- 1. Direct creation ----------
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            cancellation = serializer.save()
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
        out_serializer = CancellationSuspensionMineralRightSerializer(cancellation)
        return Response(out_serializer.data, status=status.HTTP_201_CREATED)

    # ---------- 2. Submit an existing cancellation ----------
    @extend_schema(
        request=SubmitRequestSerializer,
        responses={200: CancellationSuspensionMineralRightSerializer}
    )
    @action(detail=True, methods=['post'], url_path='submit')
    def submit(self, request, legal_entity_id=None):
        cancellation = self.get_object()

        if cancellation.status_id == 2:
            return Response(
                {'error': 'Cancellation already submitted.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        required = ['licence_id', 'legal_entity_id', 'remedy_provided']
        missing = [f for f in required if not getattr(cancellation, f, None)]
        if missing:
            return Response(
                {'error': f'Missing required fields: {", ".join(missing)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cancellation.status_id = 2
        cancellation.save()
        serializer = self.get_serializer(cancellation)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ---------- 3. Submit from draft ----------
    @extend_schema(
        request=SubmitDraftRequestSerializer,
        responses={201: CancellationSuspensionMineralRightSerializer}
    )
    @action(detail=False, methods=['post'], url_path='submit_from_draft')
    def submit_from_draft(self, request):
        draft_id = request.data.get('draft_id')
        if not draft_id:
            return Response(
                {'error': 'draft_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            draft = DraftCancellationDefault.objects.get(pk=draft_id)
        except DraftCancellationDefault.DoesNotExist:
            return Response(
                {'error': f'Draft with id {draft_id} not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        data = draft.data

        required = ['licence_id', 'legal_entity_id', 'remedy_provided']
        missing = [f for f in required if f not in data]
        if missing:
            return Response(
                {'error': f'Missing fields in draft data: {", ".join(missing)}.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate cancellation_suspension_id if not present
        if 'cancellation_suspension_id' not in data or data['cancellation_suspension_id'] is None:
            max_id = CancellationSuspensionMineralRight.objects.aggregate(
                models.Max('cancellation_suspension_id')
            )['cancellation_suspension_id__max'] or 0
            data['cancellation_suspension_id'] = max_id + 1

        try:
            cancellation = CancellationSuspensionMineralRight.objects.create(
                legal_entity_id=data['legal_entity_id'],
                cancellation_suspension_id=data['cancellation_suspension_id'],
                licence_id=data['licence_id'],
                reason_for_suspension_or_cancellation=data.get('reason_for_suspension_or_cancellation'),
                compliance_area=data.get('compliance_area'),
                comment=data.get('comment'),
                counter_comment=data.get('counter_comment'),
                remedy_provided=data['remedy_provided'],
                remedy_sufficient=data.get('remedy_sufficient'),
                deadline=data.get('deadline'),
                userid_of_issuer_of_notice=data.get('userid_of_issuer_of_notice'),
                is_approved_by_tc=data.get('is_approved_by_tc'),
                status_id=data.get('status_id', 1),
                category=data.get('category'),
                record_created_by=data.get('record_created_by'),
                guid=data.get('guid'),
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
                CancellationDefaultDocument.objects.create(
                    cancellation_suspension=cancellation,
                    document_type=doc_data.get('document_type'),
                    document_url=doc_data.get('document_url'),
                    file_name=doc_data.get('file_name', ''),
                    record_created_by=data.get('record_created_by'),
                )
        except Exception as e:
            return Response(
                {'error': f'Failed to move documents: {str(e)}. Cancellation was created but documents may be missing.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        draft.delete()
        serializer = self.get_serializer(cancellation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # ---------- (Optional) Validate documents ----------
    @action(detail=True, methods=['post'], url_path='validate_documents')
    def validate_documents(self, request, legal_entity_id=None):
        try:
            cancellation = self.get_object()
        except Exception:
            return Response(
                {'error': f'Cancellation with legal_entity_id {legal_entity_id} not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response({'message': 'Document validation successful (simulated).'})