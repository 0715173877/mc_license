import re
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import DraftQuarterlyReport, QuarterlyReport, QuarterlyReportDocument
from .serializers import (
    DraftQuarterlyReportSerializer,
    QuarterlyReportSerializer,
    QuarterlyReportCreateSerializer,
    QuarterlyReportDocumentSerializer,
)

# ---------- Request serializers ----------
class SubmitDraftRequestSerializer(serializers.Serializer):
    draft_id = serializers.IntegerField(required=True)

class SubmitRequestSerializer(serializers.Serializer):
    pass


# ---------- Draft CRUD ----------
class DraftQuarterlyReportViewSet(viewsets.ModelViewSet):
    queryset = DraftQuarterlyReport.objects.all()
    serializer_class = DraftQuarterlyReportSerializer

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


# ---------- Final Quarterly Report ----------
class QuarterlyReportViewSet(viewsets.ModelViewSet):
    queryset = QuarterlyReport.objects.all()
    serializer_class = QuarterlyReportSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return QuarterlyReportCreateSerializer
        return QuarterlyReportSerializer

    # ---------- 1. Direct creation ----------
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            report = serializer.save()
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
        out_serializer = QuarterlyReportSerializer(report)
        return Response(out_serializer.data, status=status.HTTP_201_CREATED)

    # ---------- 2. Submit an existing report ----------
    @extend_schema(
        request=SubmitRequestSerializer,
        responses={200: QuarterlyReportSerializer}
    )
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        report = self.get_object()

        if report.status_id == 2:
            return Response(
                {'error': 'Quarterly report already submitted.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate required fields
        required = ['licence_id', 'quarter', 'year']
        missing = [f for f in required if not getattr(report, f, None)]
        if missing:
            return Response(
                {'error': f'Missing required fields: {", ".join(missing)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        report.status_id = 2
        report.save()
        serializer = self.get_serializer(report)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ---------- 3. Submit from draft ----------
    @extend_schema(
        request=SubmitDraftRequestSerializer,
        responses={201: QuarterlyReportSerializer}
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
            draft = DraftQuarterlyReport.objects.get(pk=draft_id)
        except DraftQuarterlyReport.DoesNotExist:
            return Response(
                {'error': f'Draft with id {draft_id} not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        data = draft.data

        required = ['licence_id', 'quarter', 'year']
        missing = [f for f in required if f not in data]
        if missing:
            return Response(
                {'error': f'Missing fields in draft data: {", ".join(missing)}.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            report = QuarterlyReport.objects.create(
                licence_id=data['licence_id'],
                quarter=data['quarter'],
                year=data['year'],
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

        # ---------- Move documents from draft ----------
        try:
            documents = data.get('documents', [])
            for doc_data in documents:
                QuarterlyReportDocument.objects.create(
                    quarterly_report=report,
                    document_type=doc_data.get('document_type', 'Report'),
                    document_url=doc_data.get('document_url'),
                    file_name=doc_data.get('file_name', ''),
                    record_created_by=data.get('record_created_by'),
                )
        except Exception as e:
            return Response(
                {'error': f'Failed to move documents: {str(e)}. Report was created but documents may be missing.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        draft.delete()
        serializer = self.get_serializer(report)
        return Response(serializer.data, status=status.HTTP_201_CREATED)