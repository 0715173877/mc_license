import re
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import DraftEnlargement, EnlargeMineralRight
from .serializers import (
    DraftEnlargementSerializer,
    EnlargeMineralRightSerializer,
    EnlargeMineralRightCreateSerializer,
)

# ---------- Request serializers ----------
class SubmitDraftRequestSerializer(serializers.Serializer):
    draft_id = serializers.IntegerField(required=True)

class SubmitRequestSerializer(serializers.Serializer):
    pass


# ---------- Draft CRUD ----------
class DraftEnlargementViewSet(viewsets.ModelViewSet):
    queryset = DraftEnlargement.objects.all()
    serializer_class = DraftEnlargementSerializer

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


# ---------- Final Enlargement ----------
class EnlargeMineralRightViewSet(viewsets.ModelViewSet):
    queryset = EnlargeMineralRight.objects.all()
    serializer_class = EnlargeMineralRightSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return EnlargeMineralRightCreateSerializer
        return EnlargeMineralRightSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            enlargement = serializer.save()
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
        out_serializer = EnlargeMineralRightSerializer(enlargement)
        return Response(out_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        request=SubmitRequestSerializer,
        responses={200: EnlargeMineralRightSerializer}
    )
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        enlargement = self.get_object()
        if enlargement.status_id == 2:
            return Response(
                {'error': 'Enlargement already submitted.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        required = ['licence_id', 'geocoordinate']
        missing = [f for f in required if not getattr(enlargement, f, None)]
        if missing:
            return Response(
                {'error': f'Missing required fields: {", ".join(missing)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        enlargement.status_id = 2
        enlargement.save()
        serializer = self.get_serializer(enlargement)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=SubmitDraftRequestSerializer,
        responses={201: EnlargeMineralRightSerializer}
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
            draft = DraftEnlargement.objects.get(pk=draft_id)
        except DraftEnlargement.DoesNotExist:
            return Response(
                {'error': f'Draft with id {draft_id} not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        data = draft.data
        required = ['licence_id', 'geocoordinate']
        missing = [f for f in required if f not in data]
        if missing:
            return Response(
                {'error': f'Missing fields in draft data: {", ".join(missing)}.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            enlargement = EnlargeMineralRight.objects.create(
                licence_id=data['licence_id'],
                geocoordinate=data['geocoordinate'],
                development_report=data.get('development_report'),
                validation_result_id=data.get('validation_result_id'),
                application_id=data.get('application_id'),
                status_id=data.get('status_id', 1),
                application_date=data.get('application_date'),
                grant_date=data.get('grant_date'),
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

        draft.delete()
        serializer = self.get_serializer(enlargement)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def validate_shape(self, request, pk=None):
        try:
            enlargement = self.get_object()
        except Exception:
            return Response(
                {'error': f'Enlargement with id {pk} not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        # Simulate validation; replace with external service call if needed.
        return Response({'message': 'Shape validation successful (simulated).'})