import re
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import DraftComplexShape, ComplexShapeDocument
from .serializers import (
    DraftComplexShapeSerializer,
    ComplexShapeDocumentSerializer,
    ComplexShapeDocumentCreateSerializer,
)

# ---------- Request serializers ----------
class SubmitDraftRequestSerializer(serializers.Serializer):
    draft_id = serializers.IntegerField(required=True)

class SubmitRequestSerializer(serializers.Serializer):
    pass


# ---------- Draft CRUD ----------
class DraftComplexShapeViewSet(viewsets.ModelViewSet):
    queryset = DraftComplexShape.objects.all()
    serializer_class = DraftComplexShapeSerializer

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


# ---------- Final Complex Shape Document ----------
class ComplexShapeDocumentViewSet(viewsets.ModelViewSet):
    queryset = ComplexShapeDocument.objects.all()
    serializer_class = ComplexShapeDocumentSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return ComplexShapeDocumentCreateSerializer
        return ComplexShapeDocumentSerializer

    # ---------- 1. Direct creation ----------
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            doc = serializer.save()
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
        out_serializer = ComplexShapeDocumentSerializer(doc)
        return Response(out_serializer.data, status=status.HTTP_201_CREATED)

    # ---------- 2. Submit an existing document submission ----------
    @extend_schema(
        request=SubmitRequestSerializer,
        responses={200: ComplexShapeDocumentSerializer}
    )
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        doc = self.get_object()

        if doc.status_id == 2:
            return Response(
                {'error': 'Document already submitted.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        required = ['licence_id', 'document_type', 'document_url']
        missing = [f for f in required if not getattr(doc, f, None)]
        if missing:
            return Response(
                {'error': f'Missing required fields: {", ".join(missing)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        doc.status_id = 2
        doc.save()
        serializer = self.get_serializer(doc)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ---------- 3. Submit from draft ----------
    @extend_schema(
        request=SubmitDraftRequestSerializer,
        responses={201: ComplexShapeDocumentSerializer}
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
            draft = DraftComplexShape.objects.get(pk=draft_id)
        except DraftComplexShape.DoesNotExist:
            return Response(
                {'error': f'Draft with id {draft_id} not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        data = draft.data

        required = ['licence_id', 'document_type', 'document_url']
        missing = [f for f in required if f not in data]
        if missing:
            return Response(
                {'error': f'Missing fields in draft data: {", ".join(missing)}.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            doc = ComplexShapeDocument.objects.create(
                licence_id=data['licence_id'],
                document_type=data['document_type'],
                document_url=data['document_url'],
                description=data.get('description'),
                status_id=data.get('status_id', 1),
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

        draft.delete()
        serializer = self.get_serializer(doc)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # ---------- (Optional) Validate documents – placeholder ----------
    @action(detail=True, methods=['post'])
    def validate_documents(self, request, pk=None):
        try:
            doc = self.get_object()
        except Exception:
            return Response(
                {'error': f'Document with id {pk} not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response({'message': 'Document validation successful (simulated).'})