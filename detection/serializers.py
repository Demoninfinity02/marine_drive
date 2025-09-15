from rest_framework import serializers
from django.contrib.auth.models import User
from .models import DetectionSession, DetectionResult, LiveDetectionAlert, DetectionStatistics
from organisms.serializers import MarineOrganismListSerializer


class DetectionSessionListSerializer(serializers.ModelSerializer):
    """Simplified serializer for session lists"""
    
    user_name = serializers.CharField(source='user.username', read_only=True)
    duration_minutes = serializers.ReadOnlyField()
    organisms_per_ml = serializers.ReadOnlyField()
    
    class Meta:
        model = DetectionSession
        fields = [
            'session_id', 'user_name', 'start_time', 'end_time', 'is_active',
            'sample_location', 'sample_volume', 'total_organisms_detected',
            'unique_species_count', 'duration_minutes', 'organisms_per_ml'
        ]


class DetectionSessionDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual sessions"""
    
    user_name = serializers.CharField(source='user.username', read_only=True)
    duration_minutes = serializers.ReadOnlyField()
    organisms_per_ml = serializers.ReadOnlyField()
    recent_detections = serializers.SerializerMethodField()
    alerts_count = serializers.SerializerMethodField()
    
    class Meta:
        model = DetectionSession
        fields = '__all__'
        extra_fields = ['duration_minutes', 'organisms_per_ml', 'recent_detections', 'alerts_count']
    
    def get_recent_detections(self, obj):
        """Get last 10 detections from this session"""
        recent = obj.detections.select_related('organism').order_by('-detected_at')[:10]
        return DetectionResultListSerializer(recent, many=True).data
    
    def get_alerts_count(self, obj):
        """Get count of active alerts for this session"""
        return obj.alerts.filter(is_active=True).count()


class DetectionSessionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new detection sessions"""
    
    class Meta:
        model = DetectionSession
        exclude = ['session_id', 'user', 'start_time', 'end_time', 'total_frames_processed',
                  'total_organisms_detected', 'unique_species_count']
    
    def validate_sample_volume(self, value):
        """Validate sample volume is positive"""
        if value <= 0:
            raise serializers.ValidationError("Sample volume must be positive")
        return value
    
    def validate(self, data):
        """Validate coordinate ranges"""
        lat = data.get('sample_coordinates_lat')
        lng = data.get('sample_coordinates_lng')
        
        if lat is not None and (lat < -90 or lat > 90):
            raise serializers.ValidationError("Latitude must be between -90 and 90")
        
        if lng is not None and (lng < -180 or lng > 180):
            raise serializers.ValidationError("Longitude must be between -180 and 180")
        
        return data


class DetectionResultListSerializer(serializers.ModelSerializer):
    """Simplified serializer for detection result lists"""
    
    organism = MarineOrganismListSerializer(read_only=True)
    session_id = serializers.UUIDField(source='session.session_id', read_only=True)
    verified_by_name = serializers.CharField(source='verified_by.username', read_only=True)
    
    class Meta:
        model = DetectionResult
        fields = [
            'detection_id', 'session_id', 'organism', 'detected_at',
            'confidence_score', 'measured_size', 'is_verified',
            'verified_by_name', 'is_false_positive'
        ]


class DetectionResultDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual detection results"""
    
    organism = MarineOrganismListSerializer(read_only=True)
    session_location = serializers.CharField(source='session.sample_location', read_only=True)
    bbox_absolute = serializers.ReadOnlyField()
    
    class Meta:
        model = DetectionResult
        fields = '__all__'
        extra_fields = ['bbox_absolute', 'session_location']


class DetectionResultCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating detection results (from ML model)"""
    
    class Meta:
        model = DetectionResult
        exclude = ['detection_id', 'detected_at', 'is_verified', 'verified_by', 'verification_notes']
    
    def validate_confidence_score(self, value):
        """Validate confidence score is between 0 and 1"""
        if not 0 <= value <= 1:
            raise serializers.ValidationError("Confidence score must be between 0 and 1")
        return value
    
    def validate(self, data):
        """Validate bounding box coordinates"""
        bbox_fields = ['bbox_x', 'bbox_y', 'bbox_width', 'bbox_height']
        for field in bbox_fields:
            if field in data and not 0 <= data[field] <= 1:
                raise serializers.ValidationError(f"{field} must be between 0 and 1")
        
        return data


class DetectionVerificationSerializer(serializers.ModelSerializer):
    """Serializer for verifying detection results"""
    
    class Meta:
        model = DetectionResult
        fields = ['is_verified', 'is_false_positive', 'verification_notes']


class LiveDetectionAlertSerializer(serializers.ModelSerializer):
    """Serializer for live detection alerts"""
    
    session_location = serializers.CharField(source='session.sample_location', read_only=True)
    organism_name = serializers.CharField(source='organism.scientific_name', read_only=True)
    acknowledged_by_name = serializers.CharField(source='acknowledged_by.username', read_only=True)
    
    class Meta:
        model = LiveDetectionAlert
        fields = '__all__'
        extra_fields = ['session_location', 'organism_name', 'acknowledged_by_name']


class AlertAcknowledgeSerializer(serializers.Serializer):
    """Serializer for acknowledging alerts"""
    
    resolution_notes = serializers.CharField(required=False, allow_blank=True)


class DetectionStatisticsSerializer(serializers.ModelSerializer):
    """Serializer for detection statistics"""
    
    session_id = serializers.UUIDField(source='session.session_id', read_only=True)
    session_location = serializers.CharField(source='session.sample_location', read_only=True)
    
    class Meta:
        model = DetectionStatistics
        fields = '__all__'
        extra_fields = ['session_id', 'session_location']


class BulkDetectionCreateSerializer(serializers.Serializer):
    """Serializer for bulk creating detection results"""
    
    session_id = serializers.UUIDField()
    detections = DetectionResultCreateSerializer(many=True)
    
    def validate_detections(self, value):
        """Validate that we have at least one detection"""
        if not value:
            raise serializers.ValidationError("At least one detection is required")
        return value


class SessionSummarySerializer(serializers.Serializer):
    """Serializer for session summary statistics"""
    
    total_sessions = serializers.IntegerField()
    active_sessions = serializers.IntegerField()
    total_detections = serializers.IntegerField()
    unique_organisms = serializers.IntegerField()
    harmful_detections = serializers.IntegerField()
    average_confidence = serializers.FloatField()
    top_organisms = serializers.ListField()
    recent_alerts = serializers.ListField()


class EnvironmentalDataSerializer(serializers.Serializer):
    """Serializer for environmental data analysis"""
    
    temperature_stats = serializers.DictField()
    salinity_stats = serializers.DictField()
    ph_stats = serializers.DictField()
    oxygen_stats = serializers.DictField()
    environmental_correlations = serializers.DictField()


class DetectionTrendSerializer(serializers.Serializer):
    """Serializer for detection trend data"""
    
    date = serializers.DateField()
    detection_count = serializers.IntegerField()
    unique_species = serializers.IntegerField()
    harmful_count = serializers.IntegerField()
    average_confidence = serializers.FloatField()
    dominant_organism = serializers.CharField()