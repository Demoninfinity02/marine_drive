from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from detection.models import DetectionSession
import uuid


class StreamingConfiguration(models.Model):
    """Configuration settings for live video streaming"""
    
    config_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='streaming_configs')
    name = models.CharField(max_length=100, help_text="Configuration name")
    
    # Video settings
    resolution_width = models.IntegerField(default=1920)
    resolution_height = models.IntegerField(default=1080)
    fps = models.IntegerField(default=30, help_text="Frames per second")
    bitrate = models.IntegerField(default=2000, help_text="Bitrate in kbps")
    codec = models.CharField(max_length=20, default="H264")
    
    # Streaming protocol
    protocol = models.CharField(max_length=20, choices=[
        ('webrtc', 'WebRTC'),
        ('mjpeg', 'MJPEG'),
        ('rtmp', 'RTMP'),
        ('hls', 'HLS'),
    ], default='webrtc')
    
    # Detection settings
    enable_real_time_detection = models.BooleanField(default=True)
    detection_interval_ms = models.IntegerField(default=1000, help_text="Detection interval in milliseconds")
    overlay_detections = models.BooleanField(default=True)
    show_confidence_scores = models.BooleanField(default=True)
    
    # Quality settings
    auto_adjust_quality = models.BooleanField(default=True)
    min_bitrate = models.IntegerField(default=500, help_text="Minimum bitrate in kbps")
    max_bitrate = models.IntegerField(default=5000, help_text="Maximum bitrate in kbps")
    
    # Buffer settings
    buffer_size_frames = models.IntegerField(default=30)
    latency_mode = models.CharField(max_length=20, choices=[
        ('ultra_low', 'Ultra Low Latency'),
        ('low', 'Low Latency'),
        ('normal', 'Normal'),
        ('high_quality', 'High Quality'),
    ], default='low')
    
    # Metadata
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.resolution_width}x{self.resolution_height}@{self.fps}fps)"


class LiveStream(models.Model):
    """Active live streaming sessions"""
    
    stream_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    session = models.OneToOneField(DetectionSession, on_delete=models.CASCADE, related_name='live_stream')
    configuration = models.ForeignKey(StreamingConfiguration, on_delete=models.CASCADE, related_name='live_streams')
    
    # Stream status
    is_active = models.BooleanField(default=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    # Connection details
    stream_url = models.URLField(max_length=500, blank=True)
    websocket_url = models.URLField(max_length=500, blank=True)
    access_token = models.CharField(max_length=255, blank=True)
    
    # Connected viewers
    viewer_count = models.IntegerField(default=0)
    max_viewers = models.IntegerField(default=0)
    
    # Quality metrics
    current_bitrate = models.IntegerField(default=0)
    frame_drops = models.IntegerField(default=0)
    latency_ms = models.IntegerField(default=0)
    
    # Detection integration
    real_time_detections_enabled = models.BooleanField(default=True)
    last_detection_broadcast = models.DateTimeField(null=True, blank=True)
    
    # Recording
    is_recording = models.BooleanField(default=False)
    recording_file_path = models.CharField(max_length=500, blank=True)
    recording_size_mb = models.FloatField(default=0.0)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        status = "Active" if self.is_active else "Ended"
        return f"Stream {self.stream_id} - {status} ({self.viewer_count} viewers)"
    
    @property
    def duration_minutes(self):
        """Calculate stream duration in minutes"""
        end_time = self.ended_at or timezone.now()
        delta = end_time - self.started_at
        return round(delta.total_seconds() / 60, 2)


class StreamViewer(models.Model):
    """Track stream viewers and their sessions"""
    
    viewer_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    stream = models.ForeignKey(LiveStream, on_delete=models.CASCADE, related_name='viewers')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='stream_sessions')
    
    # Viewer details
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    connection_type = models.CharField(max_length=20, choices=[
        ('web', 'Web Browser'),
        ('mobile', 'Mobile App'),
        ('api', 'API Client'),
        ('embed', 'Embedded Player'),
    ], default='web')
    
    # Session details
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Quality and performance
    connection_quality = models.CharField(max_length=20, choices=[
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ], default='good')
    
    buffering_events = models.IntegerField(default=0)
    total_buffering_time_ms = models.IntegerField(default=0)
    
    # Interaction
    chat_messages_sent = models.IntegerField(default=0)
    reactions_sent = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-joined_at']
        unique_together = ['stream', 'user', 'ip_address']
    
    def __str__(self):
        user_info = self.user.username if self.user else self.ip_address
        return f"Viewer {user_info} - {self.stream.stream_id}"
    
    @property
    def session_duration_minutes(self):
        """Calculate viewer session duration in minutes"""
        end_time = self.left_at or timezone.now()
        delta = end_time - self.joined_at
        return round(delta.total_seconds() / 60, 2)


class StreamQualityMetric(models.Model):
    """Quality metrics for live streams"""
    
    stream = models.ForeignKey(LiveStream, on_delete=models.CASCADE, related_name='quality_metrics')
    
    # Timestamp
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    # Video metrics
    bitrate_kbps = models.IntegerField(default=0)
    fps_actual = models.FloatField(default=0.0)
    frame_drops = models.IntegerField(default=0)
    resolution_width = models.IntegerField(default=0)
    resolution_height = models.IntegerField(default=0)
    
    # Network metrics
    latency_ms = models.IntegerField(default=0)
    packet_loss_percent = models.FloatField(default=0.0)
    jitter_ms = models.IntegerField(default=0)
    
    # Server metrics
    cpu_usage_percent = models.FloatField(default=0.0)
    memory_usage_mb = models.FloatField(default=0.0)
    bandwidth_usage_mbps = models.FloatField(default=0.0)
    
    # Quality scores (0-100)
    video_quality_score = models.IntegerField(default=100)
    audio_quality_score = models.IntegerField(default=100)
    overall_quality_score = models.IntegerField(default=100)
    
    class Meta:
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['stream', '-recorded_at']),
        ]
    
    def __str__(self):
        return f"Quality Metric for {self.stream.stream_id} - {self.overall_quality_score}% quality"


class StreamRecording(models.Model):
    """Recorded stream sessions"""
    
    recording_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    stream = models.ForeignKey(LiveStream, on_delete=models.CASCADE, related_name='recordings')
    
    # Recording details
    filename = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    file_size_mb = models.FloatField(default=0.0)
    duration_minutes = models.FloatField(default=0.0)
    
    # Video properties
    resolution_width = models.IntegerField(default=0)
    resolution_height = models.IntegerField(default=0)
    fps = models.IntegerField(default=0)
    codec = models.CharField(max_length=20, default="H264")
    
    # Timestamps
    recording_started = models.DateTimeField()
    recording_ended = models.DateTimeField()
    processed_at = models.DateTimeField(null=True, blank=True)
    
    # Processing status
    processing_status = models.CharField(max_length=20, choices=[
        ('raw', 'Raw Recording'),
        ('processing', 'Processing'),
        ('processed', 'Processed'),
        ('failed', 'Processing Failed'),
        ('archived', 'Archived'),
    ], default='raw')
    
    # Detection highlights
    detection_highlights = models.JSONField(default=list, help_text="Timestamps of significant detections")
    organism_summary = models.JSONField(default=dict, help_text="Summary of organisms detected")
    
    # Metadata
    description = models.TextField(blank=True)
    tags = models.JSONField(default=list)
    is_public = models.BooleanField(default=False)
    
    # Access control
    download_count = models.IntegerField(default=0)
    last_accessed = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-recording_started']
    
    def __str__(self):
        return f"Recording {self.filename} - {self.duration_minutes:.1f} min"


class ChatMessage(models.Model):
    """Chat messages during live streams"""
    
    message_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    stream = models.ForeignKey(LiveStream, on_delete=models.CASCADE, related_name='chat_messages')
    viewer = models.ForeignKey(StreamViewer, on_delete=models.CASCADE, related_name='chat_messages')
    
    # Message content
    message = models.TextField(max_length=500)
    message_type = models.CharField(max_length=20, choices=[
        ('chat', 'Chat Message'),
        ('question', 'Question'),
        ('alert', 'Alert'),
        ('system', 'System Message'),
    ], default='chat')
    
    # Timestamps
    sent_at = models.DateTimeField(auto_now_add=True)
    
    # Moderation
    is_visible = models.BooleanField(default=True)
    is_flagged = models.BooleanField(default=False)
    moderated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderated_messages')
    
    # Reactions
    likes = models.IntegerField(default=0)
    reactions = models.JSONField(default=dict)
    
    class Meta:
        ordering = ['sent_at']
        indexes = [
            models.Index(fields=['stream', 'sent_at']),
        ]
    
    def __str__(self):
        return f"Message from {self.viewer} at {self.sent_at.strftime('%H:%M:%S')}"
