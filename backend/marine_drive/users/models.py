from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import RegexValidator
import uuid


class UserProfile(models.Model):
    """Extended user profile for marine research professionals"""
    
    USER_TYPES = [
        ('researcher', 'Marine Researcher'),
        ('biologist', 'Marine Biologist'),
        ('fishery_manager', 'Fishery Manager'),
        ('environmental_monitor', 'Environmental Monitor'),
        ('student', 'Student'),
        ('technician', 'Lab Technician'),
        ('consultant', 'Environmental Consultant'),
        ('government', 'Government Official'),
    ]
    
    EXPERTISE_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    # Professional information
    user_type = models.CharField(max_length=30, choices=USER_TYPES)
    organization = models.CharField(max_length=200, blank=True)
    department = models.CharField(max_length=100, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    
    # Expertise and specialization
    expertise_level = models.CharField(max_length=20, choices=EXPERTISE_LEVELS, default='beginner')
    specializations = models.JSONField(default=list, help_text="Areas of marine biology specialization")
    research_interests = models.TextField(blank=True)
    
    # Contact and location
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    country = models.CharField(max_length=100, blank=True)
    institution = models.CharField(max_length=200, blank=True)
    website = models.URLField(blank=True)
    
    # Research credentials
    degree = models.CharField(max_length=100, blank=True)
    certifications = models.JSONField(default=list)
    publications_count = models.IntegerField(default=0)
    years_experience = models.IntegerField(default=0)
    
    # Platform permissions and settings
    can_create_public_reports = models.BooleanField(default=False)
    can_moderate_content = models.BooleanField(default=False)
    can_access_advanced_analysis = models.BooleanField(default=False)
    can_export_data = models.BooleanField(default=True)
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    alert_notifications = models.BooleanField(default=True)
    weekly_reports = models.BooleanField(default=False)
    research_updates = models.BooleanField(default=True)
    
    # Profile settings
    profile_picture = models.ImageField(upload_to='profiles/pictures/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    is_public_profile = models.BooleanField(default=False)
    
    # Activity tracking
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    total_sessions = models.IntegerField(default=0)
    total_detections = models.IntegerField(default=0)
    favorite_organisms = models.JSONField(default=list)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['user__username']
        indexes = [
            models.Index(fields=['user_type']),
            models.Index(fields=['organization']),
            models.Index(fields=['expertise_level']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.user_type}"
    
    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username
    
    @property
    def detection_accuracy(self):
        """Calculate user's detection accuracy if they verify detections"""
        from detection.models import DetectionResult
        verified_detections = DetectionResult.objects.filter(verified_by=self.user)
        if verified_detections.count() == 0:
            return None
        
        correct_detections = verified_detections.filter(is_false_positive=False).count()
        return (correct_detections / verified_detections.count()) * 100


class UserPreferences(models.Model):
    """User-specific preferences for the application"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    
    # Display preferences
    default_magnification = models.CharField(max_length=50, default="400x")
    preferred_units = models.CharField(max_length=20, choices=[
        ('metric', 'Metric (μm, °C, mg/L)'),
        ('imperial', 'Imperial (mil, °F, ppm)'),
    ], default='metric')
    
    # Detection preferences
    confidence_threshold = models.FloatField(default=0.7)
    auto_save_detections = models.BooleanField(default=True)
    show_scientific_names = models.BooleanField(default=True)
    show_common_names = models.BooleanField(default=True)
    
    # Analysis preferences
    default_chart_type = models.CharField(max_length=20, choices=[
        ('bar', 'Bar Chart'),
        ('line', 'Line Chart'),
        ('pie', 'Pie Chart'),
        ('scatter', 'Scatter Plot'),
    ], default='bar')
    
    color_scheme = models.CharField(max_length=20, choices=[
        ('default', 'Default'),
        ('dark', 'Dark Mode'),
        ('high_contrast', 'High Contrast'),
        ('colorblind', 'Colorblind Friendly'),
    ], default='default')
    
    # Export preferences
    default_export_format = models.CharField(max_length=10, choices=[
        ('csv', 'CSV'),
        ('excel', 'Excel'),
        ('json', 'JSON'),
    ], default='csv')
    
    include_images_in_export = models.BooleanField(default=False)
    
    # Streaming preferences
    preferred_video_quality = models.CharField(max_length=20, choices=[
        ('480p', '480p'),
        ('720p', '720p'),
        ('1080p', '1080p'),
        ('auto', 'Auto'),
    ], default='auto')
    
    enable_real_time_overlay = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Preferences for {self.user.username}"


class ResearchGroup(models.Model):
    """Research groups and collaborations"""
    
    group_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Group management
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_groups')
    members = models.ManyToManyField(User, through='GroupMembership', related_name='research_groups')
    
    # Group settings
    is_public = models.BooleanField(default=False)
    allow_member_invites = models.BooleanField(default=True)
    require_approval = models.BooleanField(default=True)
    
    # Research focus
    research_areas = models.JSONField(default=list)
    target_organisms = models.JSONField(default=list)
    geographic_focus = models.JSONField(default=list)
    
    # Collaboration settings
    share_detection_data = models.BooleanField(default=True)
    share_analysis_results = models.BooleanField(default=True)
    collaborative_reports = models.BooleanField(default=True)
    
    # Group statistics
    total_sessions = models.IntegerField(default=0)
    total_detections = models.IntegerField(default=0)
    active_members_count = models.IntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class GroupMembership(models.Model):
    """Membership details for research groups"""
    
    ROLES = [
        ('member', 'Member'),
        ('moderator', 'Moderator'),
        ('admin', 'Administrator'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('left', 'Left Group'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(ResearchGroup, on_delete=models.CASCADE)
    
    # Membership details
    role = models.CharField(max_length=20, choices=ROLES, default='member')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Permissions
    can_create_sessions = models.BooleanField(default=True)
    can_view_all_data = models.BooleanField(default=True)
    can_export_data = models.BooleanField(default=False)
    can_invite_members = models.BooleanField(default=False)
    
    # Activity tracking
    contributions_count = models.IntegerField(default=0)
    last_activity = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'group']
        ordering = ['-joined_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.group.name} ({self.role})"


class UserActivityLog(models.Model):
    """Log of user activities for analytics and audit"""
    
    ACTIVITY_TYPES = [
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('session_start', 'Detection Session Started'),
        ('session_end', 'Detection Session Ended'),
        ('detection', 'Organism Detected'),
        ('verification', 'Detection Verified'),
        ('export', 'Data Exported'),
        ('report_generated', 'Report Generated'),
        ('stream_start', 'Stream Started'),
        ('stream_join', 'Joined Stream'),
        ('group_join', 'Joined Research Group'),
        ('settings_change', 'Settings Changed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    
    # Activity details
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    description = models.CharField(max_length=500)
    details = models.JSONField(default=dict, help_text="Additional activity details")
    
    # Context
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    session_id = models.CharField(max_length=255, blank=True)
    
    # Related objects (optional references)
    detection_session_id = models.UUIDField(null=True, blank=True)
    organism_id = models.IntegerField(null=True, blank=True)
    group_id = models.UUIDField(null=True, blank=True)
    
    # Timestamp
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['activity_type', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type} ({self.timestamp.strftime('%Y-%m-%d %H:%M')})"


class UserNotification(models.Model):
    """In-app notifications for users"""
    
    NOTIFICATION_TYPES = [
        ('detection_alert', 'Detection Alert'),
        ('harmful_organism', 'Harmful Organism Alert'),
        ('analysis_complete', 'Analysis Complete'),
        ('group_invitation', 'Group Invitation'),
        ('system_update', 'System Update'),
        ('data_export_ready', 'Data Export Ready'),
        ('weekly_report', 'Weekly Report'),
        ('stream_invitation', 'Stream Invitation'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    notification_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    
    # Notification content
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    
    # Action details
    action_url = models.URLField(blank=True, help_text="URL to navigate when notification is clicked")
    action_data = models.JSONField(default=dict, help_text="Additional data for the action")
    
    # Status
    is_read = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', '-created_at']),
            models.Index(fields=['notification_type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.username} ({'Read' if self.is_read else 'Unread'})"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
