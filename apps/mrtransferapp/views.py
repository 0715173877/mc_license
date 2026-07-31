import re
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import DraftTransfer, TransferMineralRight, TransferDocument
from .serializers import (
    DraftTransferSerializer,
    TransferMineralRightSerializer,
    TransferMineralRightCreateSerializer,
    TransferDocumentSerializer,
)

# ---------- Request serializers ----------
class SubmitDraftRequestSerializer(serializers.Serializer):
    draft_id = serializers.IntegerField(required=True)

class SubmitRequestSerializer(serializers.Serializer):
    pass  # no body needed


# ---------- Draft CRUD (step‑by‑step) ----------
class DraftTransferViewSet(viewsets.ModelViewSet):
    queryset = DraftTransfer.objects.all()
    serializer_class = DraftTransferSerializer

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


# ---------- Final Transfer (direct & draft) ----------
class TransferViewSet(viewsets.ModelViewSet):
    queryset = TransferMineralRight.objects.all()
    serializer_class = TransferMineralRightSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return TransferMineralRightCreateSerializer   # handles nested documents
        return TransferMineralRightSerializer

    # ---------- 1. Direct creation (with documents) ----------
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            transfer = serializer.save()  # creates transfer and its documents
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
        out_serializer = TransferMineralRightSerializer(transfer)
        return Response(out_serializer.data, status=status.HTTP_201_CREATED)

    # ---------- 2. Submit an existing transfer (direct or from draft) ----------
    @extend_schema(
        request=SubmitRequestSerializer,
        responses={200: TransferMineralRightSerializer}
    )
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        transfer = self.get_object()

        if transfer.status_id == 2:
            return Response(
                {'error': 'Transfer already submitted.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate required fields
        required = ['transferee_id', 'transferer_id', 'licence_id', 'transferred_share', 'transferee_type']
        missing = [f for f in required if not getattr(transfer, f, None)]
        if missing:
            return Response(
                {'error': f'Missing required fields: {", ".join(missing)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate share range
        try:
            share = float(transfer.transferred_share)
            if not (0 < share <= 100):
                raise ValueError
        except (ValueError, TypeError):
            return Response(
                {'error': 'transferred_share must be a number between 0 and 100.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update status to "submitted"
        transfer.status_id = 2
        transfer.save()
        serializer = self.get_serializer(transfer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ---------- 3. Submit from draft (draft flow) ----------
    @extend_schema(
        request=SubmitDraftRequestSerializer,
        responses={201: TransferMineralRightSerializer}
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
            draft = DraftTransfer.objects.get(pk=draft_id)
        except DraftTransfer.DoesNotExist:
            return Response(
                {'error': f'Draft with id {draft_id} not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        data = draft.data

        required = ['transferee_id', 'transferer_id', 'licence_id', 'transferred_share', 'transferee_type']
        missing = [f for f in required if f not in data]
        if missing:
            return Response(
                {'error': f'Missing fields in draft data: {", ".join(missing)}.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            share = float(data['transferred_share'])
            if not (0 < share <= 100):
                raise ValueError
        except (ValueError, TypeError):
            return Response(
                {'error': 'transferred_share must be a number between 0 and 100.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create the transfer
        try:
            transfer = TransferMineralRight.objects.create(
                transferee_id=data['transferee_id'],
                transferer_id=data['transferer_id'],
                licence_id=data['licence_id'],
                transferred_share=data['transferred_share'],
                transferee_type=data['transferee_type'],
                status_id=data.get('status_id', 1),
                effective_date=data.get('effective_date'),
                licence_status_id=data.get('licence_status_id'),
                guid=data.get('guid'),
                record_created_by=data.get('record_created_by'),
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

        # Move documents from draft.data.documents to TransferDocument
        try:
            documents = data.get('documents', [])
            for doc_data in documents:
                TransferDocument.objects.create(
                    transfer=transfer,
                    document_type=doc_data.get('document_type'),
                    document_url=doc_data.get('document_url'),
                    file_name=doc_data.get('file_name', ''),
                    record_created_by=doc_data.get('record_created_by'),
                )
            draft.delete()
        except Exception as e:
            return Response(
                {'error': f'Failed to move documents: {str(e)}. Transfer was created but documents may be missing.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        serializer = self.get_serializer(transfer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # ---------- 4. Upload a document to an existing transfer (post‑creation) ----------
    @extend_schema(
        request=None,
        responses={201: TransferDocumentSerializer}
    )
    @action(detail=True, methods=['post'])
    def upload_document(self, request, pk=None):
        try:
            transfer = self.get_object()
        except Exception:
            return Response(
                {'error': f'Transfer with id {pk} not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        document_type = request.data.get('document_type')
        document_url = request.data.get('document_url')
        if not document_type or not document_url:
            return Response(
                {'error': 'document_type and document_url are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            doc = TransferDocument.objects.create(
                transfer=transfer,
                document_type=document_type,
                document_url=document_url,
                file_name=request.data.get('file_name', document_url.split('/')[-1]),
                record_created_by=request.data.get('record_created_by')
            )
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

        serializer = TransferDocumentSerializer(doc)
        return Response(serializer.data, status=status.HTTP_201_CREATED)