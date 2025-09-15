from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Avg, Q, Sum
from django.utils import timezone
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
import logging

from .models import DetectionSession, DetectionResult, LiveDetectionAlert, DetectionStatistics
from .serializers import (
    DetectionSessionListSerializer, DetectionSessionDetailSerializer,
    DetectionSessionCreateSerializer, DetectionResultListSerializer,
    DetectionResultDetailSerializer, DetectionResultCreateSerializer,
    DetectionVerificationSerializer, LiveDetectionAlertSerializer,
    AlertAcknowledgeSerializer, DetectionStatisticsSerializer,
    BulkDetectionCreateSerializer, SessionSummarySerializer,
    EnvironmentalDataSerializer, DetectionTrendSerializer
)

logger = logging.getLogger('marine_detection')


class DetectionSessionListView(generics.ListCreateAPIView):
    """List and create detection sessions"""
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['sample_location', 'notes']
    ordering_fields = ['start_time', 'total_organisms_detected', 'sample_location']
    ordering = ['-start_time']
    
    def get_queryset(self):
        """Filter sessions by user permissions"""
        user = self.request.user
        queryset = DetectionSession.objects.select_related('user')
        
        # Users can see their own sessions and public group sessions
        if not user.is_staff:
            queryset = queryset.filter(user=user)
        
        # Filter by active/inactive
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(start_time__gte=start_date)
        if end_date:
            queryset = queryset.filter(start_time__lte=end_date)
        
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DetectionSessionCreateSerializer
        return DetectionSessionListSerializer
    
    def perform_create(self, serializer):
        """Set the user and log session creation"""
        session = serializer.save(user=self.request.user)
        logger.info(f"New detection session created: {session.session_id} by {self.request.user.username}")


class DetectionSessionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a detection session"""
    serializer_class = DetectionSessionDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'session_id'
    
    def get_queryset(self):
        """Only allow access to user's own sessions or staff"""
        user = self.request.user
        if user.is_staff:
            return DetectionSession.objects.all()
        return DetectionSession.objects.filter(user=user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def end_detection_session(request, session_id):
    """End a detection session and calculate final statistics"""
    session = get_object_or_404(
        DetectionSession,
        session_id=session_id,
        user=request.user,
        is_active=True
    )
    
    session.end_time = timezone.now()
    session.is_active = False
    
    # Calculate final statistics
    detections = session.detections.all()
    session.total_organisms_detected = detections.count()
    session.unique_species_count = detections.values('organism').distinct().count()
    
    session.save()
    
    # Create or update statistics
    stats, created = DetectionStatistics.objects.get_or_create(session=session)
    stats.calculate_statistics()
    
    logger.info(f"Detection session ended: {session_id} with {session.total_organisms_detected} detections")
    
    return Response({
        'message': 'Session ended successfully',
        'session_id': session_id,
        'duration_minutes': session.duration_minutes,
        'total_detections': session.total_organisms_detected,
        'unique_species': session.unique_species_count
    })


class DetectionResultListView(generics.ListCreateAPIView):
    """List and create detection results"""
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['detected_at', 'confidence_score', 'measured_size']
    ordering = ['-detected_at']
    
    def get_queryset(self):
        """Filter results by session and user permissions"""
        user = self.request.user
        queryset = DetectionResult.objects.select_related('organism', 'session')
        
        # Filter by session if provided
        session_id = self.request.query_params.get('session_id')
        if session_id:
            if user.is_staff:
                queryset = queryset.filter(session__session_id=session_id)
            else:
                queryset = queryset.filter(session__session_id=session_id, session__user=user)
        else:
            # Show only user's detections unless staff
            if not user.is_staff:
                queryset = queryset.filter(session__user=user)
        
        # Filter by organism
        organism_id = self.request.query_params.get('organism_id')
        if organism_id:
            queryset = queryset.filter(organism_id=organism_id)
        
        # Filter by verification status
        is_verified = self.request.query_params.get('is_verified')
        if is_verified is not None:
            queryset = queryset.filter(is_verified=is_verified.lower() == 'true')
        
        # Filter by confidence threshold
        min_confidence = self.request.query_params.get('min_confidence')
        if min_confidence:
            try:
                queryset = queryset.filter(confidence_score__gte=float(min_confidence))
            except ValueError:
                pass
        
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DetectionResultCreateSerializer
        return DetectionResultListSerializer
    
    def perform_create(self, serializer):
        """Log detection creation"""
        detection = serializer.save()
        logger.info(f"New detection: {detection.organism.scientific_name} in session {detection.session.session_id}")


class DetectionResultDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a detection result"""
    serializer_class = DetectionResultDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'detection_id'
    
    def get_queryset(self):
        """Only allow access to user's own detections or staff"""
        user = self.request.user
        if user.is_staff:
            return DetectionResult.objects.all()
        return DetectionResult.objects.filter(session__user=user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_detection(request, detection_id):
    """Verify or flag a detection result"""
    detection = get_object_or_404(
        DetectionResult,
        detection_id=detection_id
    )
    
    # Check permissions
    if not request.user.is_staff and detection.session.user != request.user:
        return Response(
            {'error': 'Permission denied'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = DetectionVerificationSerializer(detection, data=request.data, partial=True)
    if serializer.is_valid():
        detection = serializer.save(verified_by=request.user)
        
        # Update detection profile statistics
        profile = detection.organism.detection_profile
        if detection.is_verified:
            if detection.is_false_positive:
                profile.false_positives += 1
            else:
                profile.successful_identifications += 1
        profile.save()
        
        return Response({
            'message': 'Detection verified successfully',
            'detection_id': detection_id,
            'is_verified': detection.is_verified,
            'is_false_positive': detection.is_false_positive
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_create_detections(request):
    """Bulk create detection results from ML model"""
    serializer = BulkDetectionCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    session = get_object_or_404(DetectionSession, session_id=data['session_id'])
    
    # Check permissions
    if not request.user.is_staff and session.user != request.user:
        return Response(
            {'error': 'Permission denied'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    created_detections = []
    errors = []
    
    for i, detection_data in enumerate(data['detections']):
        detection_data['session'] = session.id
        detection_serializer = DetectionResultCreateSerializer(data=detection_data)
        
        if detection_serializer.is_valid():
            try:
                detection = detection_serializer.save()
                created_detections.append(detection.detection_id)
                
                # Update detection profile
                profile, created = detection.organism.detection_profile
                profile.total_detections += 1
                profile.last_detection = timezone.now()
                profile.save()
                
            except Exception as e:
                errors.append({'index': i, 'error': str(e)})
        else:
            errors.append({'index': i, 'validation_errors': detection_serializer.errors})
    
    # Update session statistics
    session.total_frames_processed += 1
    session.total_organisms_detected = session.detections.count()
    session.unique_species_count = session.detections.values('organism').distinct().count()
    session.save()
    
    return Response({
        'created_count': len(created_detections),
        'error_count': len(errors),
        'created_detections': created_detections,
        'errors': errors
    })


class LiveDetectionAlertListView(generics.ListCreateAPIView):
    """List and create live detection alerts"""
    serializer_class = LiveDetectionAlertSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter alerts by user permissions"""
        user = self.request.user
        queryset = LiveDetectionAlert.objects.select_related('session', 'organism')
        
        if not user.is_staff:
            queryset = queryset.filter(session__user=user)
        
        # Filter by active/resolved
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter by severity
        severity = self.request.query_params.get('severity')
        if severity:
            queryset = queryset.filter(severity=severity)
        
        return queryset


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def acknowledge_alert(request, alert_id):
    """Acknowledge and optionally resolve an alert"""
    alert = get_object_or_404(LiveDetectionAlert, alert_id=alert_id)
    
    # Check permissions
    if not request.user.is_staff and alert.session.user != request.user:
        return Response(
            {'error': 'Permission denied'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = AlertAcknowledgeSerializer(data=request.data)
    if serializer.is_valid():
        alert.acknowledged_at = timezone.now()
        alert.acknowledged_by = request.user
        alert.is_resolved = True
        alert.resolution_notes = serializer.validated_data.get('resolution_notes', '')
        alert.save()
        
        return Response({
            'message': 'Alert acknowledged successfully',
            'alert_id': alert_id
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def session_summary(request):
    """Get summary statistics for user's sessions"""
    user = request.user
    queryset = DetectionSession.objects.filter(user=user) if not user.is_staff else DetectionSession.objects.all()
    
    summary = {
        'total_sessions': queryset.count(),
        'active_sessions': queryset.filter(is_active=True).count(),
        'total_detections': DetectionResult.objects.filter(session__in=queryset).count(),
        'unique_organisms': DetectionResult.objects.filter(session__in=queryset).values('organism').distinct().count(),
        'harmful_detections': DetectionResult.objects.filter(
            session__in=queryset,
            organism__is_harmful=True
        ).count(),
        'average_confidence': DetectionResult.objects.filter(
            session__in=queryset
        ).aggregate(avg=Avg('confidence_score'))['avg'] or 0,
        'top_organisms': list(
            DetectionResult.objects.filter(session__in=queryset)
            .values('organism__scientific_name', 'organism__common_name')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        ),
        'recent_alerts': list(
            LiveDetectionAlert.objects.filter(session__in=queryset, is_active=True)
            .order_by('-created_at')[:5]
            .values('alert_type', 'severity', 'title', 'created_at')
        )
    }
    
    serializer = SessionSummarySerializer(summary)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def detection_trends(request):
    """Get detection trends over time"""
    user = request.user
    days = int(request.query_params.get('days', 30))
    
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    # Get sessions in date range
    sessions = DetectionSession.objects.filter(
        start_time__range=[start_date, end_date]
    )
    
    if not user.is_staff:
        sessions = sessions.filter(user=user)
    
    # Group by date and calculate metrics
    trends = []
    current_date = start_date.date()
    
    while current_date <= end_date.date():
        day_sessions = sessions.filter(start_time__date=current_date)
        day_detections = DetectionResult.objects.filter(session__in=day_sessions)
        
        trend_data = {
            'date': current_date,
            'detection_count': day_detections.count(),
            'unique_species': day_detections.values('organism').distinct().count(),
            'harmful_count': day_detections.filter(organism__is_harmful=True).count(),
            'average_confidence': day_detections.aggregate(avg=Avg('confidence_score'))['avg'] or 0,
            'dominant_organism': ''
        }
        
        # Find most detected organism
        top_organism = (
            day_detections.values('organism__scientific_name')
            .annotate(count=Count('id'))
            .order_by('-count')
            .first()
        )
        
        if top_organism:
            trend_data['dominant_organism'] = top_organism['organism__scientific_name']
        
        trends.append(trend_data)
        current_date += timedelta(days=1)
    
    serializer = DetectionTrendSerializer(trends, many=True)
    return Response(serializer.data)
