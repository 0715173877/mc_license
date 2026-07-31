import re
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import DraftExtension, ExtensionToCommenceMining
from .serializers import (
    DraftExtensionSerializer,
    ExtensionToCommenceMiningSerializer,
    ExtensionToCommenceMiningCreateSerializer,
)

# ---------- Request serializers ----------
class SubmitDraftRequestSerializer(serializers.Serializer):
    draft_id = serializers.IntegerField(required=True)

class SubmitRequestSerializer(serializers.Serializer):
    pass


# ---------- Draft CRUD ----------
class DraftExtensionViewSet(viewsets.ModelViewSet):
    queryset = DraftExtension.objects.all()
    serializer_class = DraftExtensionSerializer

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


# ---------- Final Extension ----------
class ExtensionToCommenceMiningViewSet(viewsets.ModelViewSet):
    queryset = ExtensionToCommenceMining.objects.all()
    serializer_class = ExtensionToCommenceMiningSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return ExtensionToCommenceMiningCreateSerializer
        return ExtensionToCommenceMiningSerializer

    # ---------- 1. Direct creation ----------
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            extension = serializer.save()
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
        out_serializer = ExtensionToCommenceMiningSerializer(extension)
        return Response(out_serializer.data, status=status.HTTP_201_CREATED)

    # ---------- 2. Submit an existing extension ----------
    @extend_schema(
        request=SubmitRequestSerializer,
        responses={200: ExtensionToCommenceMiningSerializer}
    )
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        extension = self.get_object()

        if extension.status_id == 2:
            return Response(
                {'error': 'Extension already submitted.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate required fields
        required = ['licence_id', 'extension_reason', 'extension_duration']
        missing = [f for f in required if not getattr(extension, f, None)]
        if missing:
            return Response(
                {'error': f'Missing required fields: {", ".join(missing)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        extension.status_id = 2
        extension.save()
        serializer = self.get_serializer(extension)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ---------- 3. Submit from draft ----------
    @extend_schema(
        request=SubmitDraftRequestSerializer,
        responses={201: ExtensionToCommenceMiningSerializer}
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
            draft = DraftExtension.objects.get(pk=draft_id)
        except DraftExtension.DoesNotExist:
            return Response(
                {'error': f'Draft with id {draft_id} not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        data = draft.data

        required = ['licence_id', 'extension_reason', 'extension_duration']
        missing = [f for f in required if f not in data]
        if missing:
            return Response(
                {'error': f'Missing fields in draft data: {", ".join(missing)}.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            extension = ExtensionToCommenceMining.objects.create(
                licence_id=data['licence_id'],
                extension_reason=data['extension_reason'],
                extension_duration=data['extension_duration'],
                status_id=data.get('status_id', 1),
                application_date=data.get('application_date'),
                issued_date=data.get('issued_date'),
                legal_entity_id=data.get('legal_entity_id'),
                record_created_by=data.get('record_created_by'),
                extension_certificate_number=data.get('extension_certificate_number'),
                expiry_date=data.get('expiry_date'),
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

        # Documents are stored in the draft JSON – no final document table.
        # Just delete the draft.
        draft.delete()

        serializer = self.get_serializer(extension)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # ---------- (Optional) Validate documents – placeholder ----------
    @action(detail=True, methods=['post'])
    def validate_documents(self, request, pk=None):
        try:
            extension = self.get_object()
        except Exception:
            return Response(
                {'error': f'Extension with id {pk} not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response({'message': 'Document validation successful (simulated).'})