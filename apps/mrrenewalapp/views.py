import re
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import DraftRenewal, Renewal, RenewalDocument
from .serializers import (
    DraftRenewalSerializer,
    RenewalSerializer,
    RenewalCreateSerializer,
    RenewalDocumentSerializer,
)

# ---------- Request serializers ----------
class SubmitDraftRequestSerializer(serializers.Serializer):
    draft_id = serializers.IntegerField(required=True)

class SubmitRequestSerializer(serializers.Serializer):
    pass


# ---------- Draft CRUD ----------
class DraftRenewalViewSet(viewsets.ModelViewSet):
    queryset = DraftRenewal.objects.all()
    serializer_class = DraftRenewalSerializer

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


# ---------- Final Renewal ----------
class RenewalViewSet(viewsets.ModelViewSet):
    queryset = Renewal.objects.all()
    serializer_class = RenewalSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return RenewalCreateSerializer
        return RenewalSerializer

    # ---------- 1. Direct creation ----------
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            renewal = serializer.save()
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
        out_serializer = RenewalSerializer(renewal)
        return Response(out_serializer.data, status=status.HTTP_201_CREATED)

    # ---------- 2. Submit an existing renewal ----------
    @extend_schema(
        request=SubmitRequestSerializer,
        responses={200: RenewalSerializer}
    )
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        renewal = self.get_object()

        if renewal.status_id == 2:
            return Response(
                {'error': 'Renewal already submitted.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate required fields
        required = ['licence_id', 'number_of_years']
        missing = [f for f in required if not getattr(renewal, f, None)]
        if missing:
            return Response(
                {'error': f'Missing required fields: {", ".join(missing)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # If not same shape, coordinates must be provided
        if not renewal.is_same_shape and not renewal.new_coordinates:
            return Response(
                {'error': 'New coordinates are required when "Is Same Shape" is No.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        renewal.status_id = 2
        renewal.save()
        serializer = self.get_serializer(renewal)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ---------- 3. Submit from draft ----------
    @extend_schema(
        request=SubmitDraftRequestSerializer,
        responses={201: RenewalSerializer}
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
            draft = DraftRenewal.objects.get(pk=draft_id)
        except DraftRenewal.DoesNotExist:
            return Response(
                {'error': f'Draft with id {draft_id} not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        data = draft.data

        required = ['licence_id', 'number_of_years']
        missing = [f for f in required if f not in data]
        if missing:
            return Response(
                {'error': f'Missing fields in draft data: {", ".join(missing)}.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # If not same shape, coordinates must be provided
        is_same_shape = data.get('is_same_shape', True)
        if not is_same_shape and not data.get('new_coordinates'):
            return Response(
                {'error': 'New coordinates are required when "Is Same Shape" is No.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            renewal = Renewal.objects.create(
                licence_id=data['licence_id'],
                is_same_shape=is_same_shape,
                new_coordinates=data.get('new_coordinates'),
                number_of_years=data['number_of_years'],
                status_id=data.get('status_id', 1),
                legal_entity_id=data.get('legal_entity_id'),
                record_created_by=data.get('record_created_by'),
                guid=data.get('guid'),
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

        # ---------- Move documents from draft ----------
        try:
            documents = data.get('documents', [])
            for doc_data in documents:
                RenewalDocument.objects.create(
                    renewal=renewal,
                    document_type=doc_data.get('document_type'),
                    document_url=doc_data.get('document_url'),
                    file_name=doc_data.get('file_name', ''),
                    record_created_by=data.get('record_created_by'),
                )
        except Exception as e:
            return Response(
                {'error': f'Failed to move documents: {str(e)}. Renewal was created but documents may be missing.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        draft.delete()
        serializer = self.get_serializer(renewal)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # ---------- (Optional) Validate documents – placeholder ----------
    @action(detail=True, methods=['post'])
    def validate_documents(self, request, pk=None):
        try:
            renewal = self.get_object()
        except Exception:
            return Response(
                {'error': f'Renewal with id {pk} not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response({'message': 'Document validation successful (simulated).'})