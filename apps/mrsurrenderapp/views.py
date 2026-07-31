import re
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import DraftSurrender, SurrenderMineralRight
from .serializers import (
    DraftSurrenderSerializer,
    SurrenderMineralRightSerializer,
    SurrenderMineralRightCreateSerializer,
)

# ---------- Request serializers ----------
class SubmitDraftRequestSerializer(serializers.Serializer):
    draft_id = serializers.IntegerField(required=True)

class SubmitRequestSerializer(serializers.Serializer):
    pass


# ---------- Draft CRUD ----------
class DraftSurrenderViewSet(viewsets.ModelViewSet):
    queryset = DraftSurrender.objects.all()
    serializer_class = DraftSurrenderSerializer

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


# ---------- Final Surrender ----------
class SurrenderMineralRightViewSet(viewsets.ModelViewSet):
    queryset = SurrenderMineralRight.objects.all()
    serializer_class = SurrenderMineralRightSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return SurrenderMineralRightCreateSerializer
        return SurrenderMineralRightSerializer

    # ---------- 1. Direct creation ----------
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            surrender = serializer.save()
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
        out_serializer = SurrenderMineralRightSerializer(surrender)
        return Response(out_serializer.data, status=status.HTTP_201_CREATED)

    # ---------- 2. Submit an existing surrender ----------
    @extend_schema(
        request=SubmitRequestSerializer,
        responses={200: SurrenderMineralRightSerializer}
    )
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        surrender = self.get_object()

        if surrender.status_id == 2:
            return Response(
                {'error': 'Surrender already submitted.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate required fields
        required = ['licence_id', 'reason_for_surrender', 'effective_surrender_date']
        missing = [f for f in required if not getattr(surrender, f, None)]
        if missing:
            return Response(
                {'error': f'Missing required fields: {", ".join(missing)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate surrender type: if Partial, both coordinate fields required; if Total, only remaining area maybe? We'll keep it flexible.
        surrender.status_id = 2
        surrender.save()
        serializer = self.get_serializer(surrender)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ---------- 3. Submit from draft ----------
    @extend_schema(
        request=SubmitDraftRequestSerializer,
        responses={201: SurrenderMineralRightSerializer}
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
            draft = DraftSurrender.objects.get(pk=draft_id)
        except DraftSurrender.DoesNotExist:
            return Response(
                {'error': f'Draft with id {draft_id} not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        data = draft.data

        required = ['licence_id', 'reason_for_surrender', 'effective_surrender_date', 'surrender_type']
        missing = [f for f in required if f not in data]
        if missing:
            return Response(
                {'error': f'Missing fields in draft data: {", ".join(missing)}.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate date logic (not less than 3 months before effective date) – we can do later.

        try:
            surrender = SurrenderMineralRight.objects.create(
                licence_id=data['licence_id'],
                reason_for_surrender=data['reason_for_surrender'],
                effective_surrender_date=data['effective_surrender_date'],
                shape_validation_result_id=data.get('shape_validation_result_id'),
                status_id=data.get('status_id', 1),
                record_created_by=data.get('record_created_by'),
                legal_entity_id=data.get('legal_entity_id'),
                guid=data.get('guid'),
                geo_coordinate_for_remaining_area=data.get('geo_coordinate_for_remaining_area'),
                geo_coordinates_for_surrender_area=data.get('geo_coordinates_for_surrender_area'),
                surrender_type=data['surrender_type'],
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

        # No documents to move – but we can store them in the draft data if needed; for now just delete draft.
        draft.delete()

        serializer = self.get_serializer(surrender)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # ---------- (Optional) Validate coordinates – placeholder ----------
    @action(detail=True, methods=['post'])
    def validate_coordinates(self, request, pk=None):
        try:
            surrender = self.get_object()
        except Exception:
            return Response(
                {'error': f'Surrender with id {pk} not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        # Simulate validation; replace with external call.
        return Response({'message': 'Coordinate validation successful (simulated).'})