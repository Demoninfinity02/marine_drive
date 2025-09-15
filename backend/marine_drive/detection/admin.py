from django.contrib import admin
from .models import DetectionSession, DetectionResult, LiveDetectionAlert, DetectionStatistics


@admin.register(DetectionSession)
class DetectionSessionAdmin(admin.ModelAdmin):
    list_display = [
        'session_id', 'user', 'sample_location', 'start_time', 'end_time',
        'is_active', 'total_organisms_detected', 'unique_species_count'
    ]
    list_filter = ['is_active', 'start_time', 'user']
    search_fields = ['session_id', 'sample_location', 'user__username', 'notes']
    readonly_fields = [
        'session_id', 'start_time', 'total_frames_processed',
        'total_organisms_detected', 'unique_species_count'
    ]
    date_hierarchy = 'start_time'


@admin.register(DetectionResult)
class DetectionResultAdmin(admin.ModelAdmin):
    list_display = [
        'detection_id', 'session', 'organism', 'detected_at',
        'confidence_score', 'is_verified', 'is_false_positive'
    ]
    list_filter = [
        'detected_at', 'is_verified', 'is_false_positive', 'organism',
        'confidence_score'
    ]
    search_fields = [
        'detection_id', 'organism__scientific_name', 'session__session_id'
    ]
    readonly_fields = ['detection_id', 'detected_at']
    date_hierarchy = 'detected_at'


@admin.register(LiveDetectionAlert)
class LiveDetectionAlertAdmin(admin.ModelAdmin):
    list_display = [
        'alert_id', 'session', 'alert_type', 'severity', 'title',
        'created_at', 'is_active', 'is_resolved'
    ]
    list_filter = [
        'alert_type', 'severity', 'is_active', 'is_resolved', 'created_at'
    ]
    search_fields = ['alert_id', 'title', 'message']
    readonly_fields = ['alert_id', 'created_at']
    date_hierarchy = 'created_at'


@admin.register(DetectionStatistics)
class DetectionStatisticsAdmin(admin.ModelAdmin):
    list_display = [
        'session', 'total_concentration_per_ml', 'harmful_organisms_per_ml',
        'biodiversity_index', 'average_confidence_score', 'calculated_at'
    ]
    list_filter = ['calculated_at']
    search_fields = ['session__session_id']
    readonly_fields = ['calculated_at']
