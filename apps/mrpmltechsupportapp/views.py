import re
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import DraftPmlTechSupport, PmlTechnicalSupport, PmlTechSupportDocument
from .serializers import (
    DraftPmlTechSupportSerializer,
    PmlTechnicalSupportSerializer,
    PmlTechnicalSupportCreateSerializer,
    PmlTechSupportDocumentSerializer,
)

# ---------- Request serializers ----------
class SubmitDraftRequestSerializer(serializers.Serializer):
    draft_id = serializers.IntegerField(required=True)

class SubmitRequestSerializer(serializers.Serializer):
    pass


# ---------- Draft CRUD ----------
class DraftPmlTechSupportViewSet(viewsets.ModelViewSet):
    queryset = DraftPmlTechSupport.objects.all()
    serializer_class = DraftPmlTechSupportSerializer

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


# ---------- Final PML Technical Support (Initial) ----------
class PmlTechnicalSupportViewSet(viewsets.ModelViewSet):
    queryset = PmlTechnicalSupport.objects.all()
    serializer_class = PmlTechnicalSupportSerializer

    def get_queryset(self):
        # Return only initial applications
        return PmlTechnicalSupport.objects.filter(is_fresh_application=True)

    def get_serializer_class(self):
        if self.action == 'create':
            return PmlTechnicalSupportCreateSerializer
        return PmlTechnicalSupportSerializer

    # ---------- 1. Direct creation ----------
    def create(self, request, *args, **kwargs):
        # Ensure it is a fresh application
        if 'is_fresh_application' not in request.data:
            request.data['is_fresh_application'] = True
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            pml_ts = serializer.save()
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
        out_serializer = PmlTechnicalSupportSerializer(pml_ts)
        return Response(out_serializer.data, status=status.HTTP_201_CREATED)

    # ---------- 2. Submit an existing ----------
    @extend_schema(
        request=SubmitRequestSerializer,
        responses={200: PmlTechnicalSupportSerializer}
    )
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        pml_ts = self.get_object()

        if pml_ts.status_id == 2:
            return Response(
                {'error': 'PML Technical Support already submitted.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        required = ['licence_id', 'ts_type', 'ts_provider_category', 'legal_entity_id']
        missing = [f for f in required if not getattr(pml_ts, f, None)]
        if missing:
            return Response(
                {'error': f'Missing required fields: {", ".join(missing)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        pml_ts.status_id = 2
        pml_ts.save()
        serializer = self.get_serializer(pml_ts)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ---------- 3. Submit from draft ----------
    @extend_schema(
        request=SubmitDraftRequestSerializer,
        responses={201: PmlTechnicalSupportSerializer}
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
            draft = DraftPmlTechSupport.objects.get(pk=draft_id)
        except DraftPmlTechSupport.DoesNotExist:
            return Response(
                {'error': f'Draft with id {draft_id} not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        data = draft.data
        data['is_fresh_application'] = True

        required = ['licence_id', 'ts_type', 'ts_provider_category', 'legal_entity_id']
        missing = [f for f in required if f not in data]
        if missing:
            return Response(
                {'error': f'Missing fields in draft data: {", ".join(missing)}.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            pml_ts = PmlTechnicalSupport.objects.create(
                licence_id=data['licence_id'],
                ts_type=data['ts_type'],
                ts_provider_category=data['ts_provider_category'],
                legal_entity_id=data['legal_entity_id'],
                technical_support_certificate_number=data.get('technical_support_certificate_number'),
                issued_date=data.get('issued_date'),
                duration=data.get('duration'),
                expiry_date=data.get('expiry_date'),
                is_fresh_application=True,
                status_id=data.get('status_id', 1),
                mineral_right_id=data.get('mineral_right_id'),
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
                PmlTechSupportDocument.objects.create(
                    pml_technical_support=pml_ts,
                    document_type=doc_data.get('document_type'),
                    document_url=doc_data.get('document_url'),
                    file_name=doc_data.get('file_name', ''),
                    record_created_by=data.get('record_created_by'),
                )
        except Exception as e:
            return Response(
                {'error': f'Failed to move documents: {str(e)}. Pml TS was created but documents may be missing.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        draft.delete()
        serializer = self.get_serializer(pml_ts)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # ---------- (Optional) Validate documents – placeholder ----------
    @action(detail=True, methods=['post'])
    def validate_documents(self, request, pk=None):
        try:
            pml_ts = self.get_object()
        except Exception:
            return Response(
                {'error': f'PML Technical Support with id {pk} not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response({'message': 'Document validation successful (simulated).'})