from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from organisms.models import MarineOrganism
import uuid


class DetectionSession(models.Model):
    """Represents a microscope detection session"""
    session_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='detection_sessions')
    
    # Session metadata
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Sample information
    sample_location = models.CharField(max_length=200, help_text="Geographic location of sample")
    sample_coordinates_lat = models.FloatField(null=True, blank=True)
    sample_coordinates_lng = models.FloatField(null=True, blank=True)
    sample_depth = models.FloatField(null=True, blank=True, help_text="Depth in meters")
    sample_volume = models.FloatField(help_text="Sample volume in milliliters", validators=[MinValueValidator(0.1)])
    
    # Environmental conditions
    water_temperature = models.FloatField(null=True, blank=True, help_text="Temperature in Celsius")
    salinity = models.FloatField(null=True, blank=True, help_text="Salinity in PSU")
    ph_level = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(14)])
    dissolved_oxygen = models.FloatField(null=True, blank=True, help_text="DO in mg/L")
    
    # Technical settings
    microscope_magnification = models.CharField(max_length=50, default="400x")
    ml_model_version = models.CharField(max_length=50, default="v1.0")
    confidence_threshold = models.FloatField(default=0.7, validators=[MinValueValidator(0.1), MaxValueValidator(1.0)])
    
    # Session statistics
    total_frames_processed = models.IntegerField(default=0)
    total_organisms_detected = models.IntegerField(default=0)
    unique_species_count = models.IntegerField(default=0)
    
    # Notes and comments
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['user', '-start_time']),
            models.Index(fields=['sample_location']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"Session {self.session_id} - {self.sample_location} ({self.start_time.strftime('%Y-%m-%d %H:%M')})"
    
    @property
    def duration_minutes(self):
        """Calculate session duration in minutes"""
        if self.end_time:
            delta = self.end_time - self.start_time
            return round(delta.total_seconds() / 60, 2)
        return None
    
    @property
    def organisms_per_ml(self):
        """Calculate organism concentration per milliliter"""
        if self.sample_volume > 0:
            return round(self.total_organisms_detected / self.sample_volume, 2)
        return 0


class DetectionResult(models.Model):
    """Individual organism detection result"""
    detection_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    session = models.ForeignKey(DetectionSession, on_delete=models.CASCADE, related_name='detections')
    organism = models.ForeignKey(MarineOrganism, on_delete=models.CASCADE, related_name='detection_results')
    
    # Detection metadata
    detected_at = models.DateTimeField(auto_now_add=True)
    frame_number = models.IntegerField(help_text="Video frame number where detected")
    
    # ML model results
    confidence_score = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    model_version = models.CharField(max_length=50, default="v1.0")
    
    # Bounding box coordinates (normalized 0-1)
    bbox_x = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    bbox_y = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    bbox_width = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    bbox_height = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    
    # Measured characteristics
    measured_size = models.FloatField(null=True, blank=True, help_text="Size in micrometers")
    measured_area = models.FloatField(null=True, blank=True, help_text="Area in square micrometers")
    
    # Image data
    detection_image = models.ImageField(upload_to='detections/images/', null=True, blank=True)
    cropped_organism_image = models.ImageField(upload_to='detections/crops/', null=True, blank=True)
    
    # Verification and quality control
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_detections')
    verification_notes = models.TextField(blank=True)
    is_false_positive = models.BooleanField(default=False)
    
    # Additional features extracted by ML model
    features_json = models.JSONField(default=dict, help_text="Additional features extracted by ML model")
    
    class Meta:
        ordering = ['-detected_at']
        indexes = [
            models.Index(fields=['session', '-detected_at']),
            models.Index(fields=['organism', '-detected_at']),
            models.Index(fields=['confidence_score']),
            models.Index(fields=['is_verified']),
        ]
    
    def __str__(self):
        return f"{self.organism.scientific_name} - {self.confidence_score:.2f} confidence"
    
    @property
    def bbox_absolute(self):
        """Convert normalized bounding box to absolute coordinates"""
        return {
            'x': self.bbox_x,
            'y': self.bbox_y,
            'width': self.bbox_width,
            'height': self.bbox_height
        }


class LiveDetectionAlert(models.Model):
    """Real-time alerts for harmful organisms or unusual concentrations"""
    ALERT_TYPES = [
        ('harmful_organism', 'Harmful Organism Detected'),
        ('high_concentration', 'High Organism Concentration'),
        ('unusual_species', 'Unusual Species Detected'),
        ('bloom_warning', 'Potential Algal Bloom'),
        ('environmental_anomaly', 'Environmental Parameter Anomaly'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    alert_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    session = models.ForeignKey(DetectionSession, on_delete=models.CASCADE, related_name='alerts')
    
    # Alert details
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Related data
    organism = models.ForeignKey(MarineOrganism, on_delete=models.CASCADE, null=True, blank=True)
    detection_count = models.IntegerField(default=1)
    concentration_per_ml = models.FloatField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    acknowledged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_resolved = models.BooleanField(default=False)
    resolution_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['session', '-created_at']),
            models.Index(fields=['alert_type', 'severity']),
            models.Index(fields=['is_active', 'is_resolved']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.severity.upper()} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


class DetectionStatistics(models.Model):
    """Aggregated statistics for detection sessions"""
    session = models.OneToOneField(DetectionSession, on_delete=models.CASCADE, related_name='statistics')
    
    # Organism counts by taxonomy
    organisms_by_kingdom = models.JSONField(default=dict)
    organisms_by_phylum = models.JSONField(default=dict)
    organisms_by_class = models.JSONField(default=dict)
    organisms_by_genus = models.JSONField(default=dict)
    
    # Concentration statistics
    total_concentration_per_ml = models.FloatField(default=0.0)
    harmful_organisms_per_ml = models.FloatField(default=0.0)
    biodiversity_index = models.FloatField(null=True, blank=True, help_text="Shannon diversity index")
    
    # Environmental correlations
    temperature_organism_correlation = models.JSONField(default=dict)
    salinity_organism_correlation = models.JSONField(default=dict)
    
    # Time-based patterns
    detection_rate_per_minute = models.JSONField(default=dict)
    peak_detection_time = models.DateTimeField(null=True, blank=True)
    
    # Quality metrics
    average_confidence_score = models.FloatField(default=0.0)
    verification_rate = models.FloatField(default=0.0, help_text="Percentage of verified detections")
    
    # Metadata
    calculated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Statistics for {self.session.session_id}"
    
    def calculate_statistics(self):
        """Recalculate all statistics for the session"""
        detections = self.session.detections.all()
        
        # Basic counts
        total_count = detections.count()
        if total_count == 0:
            return
        
        # Calculate concentrations
        self.total_concentration_per_ml = total_count / self.session.sample_volume
        harmful_count = detections.filter(organism__is_harmful=True).count()
        self.harmful_organisms_per_ml = harmful_count / self.session.sample_volume
        
        # Calculate average confidence
        avg_confidence = detections.aggregate(avg=models.Avg('confidence_score'))['avg']
        self.average_confidence_score = avg_confidence or 0.0
        
        # Calculate verification rate
        verified_count = detections.filter(is_verified=True).count()
        self.verification_rate = (verified_count / total_count) * 100 if total_count > 0 else 0
        
        # Taxonomy distribution
        self.organisms_by_kingdom = self._calculate_taxonomy_distribution(detections, 'organism__kingdom__name')
        self.organisms_by_phylum = self._calculate_taxonomy_distribution(detections, 'organism__phylum__name')
        self.organisms_by_class = self._calculate_taxonomy_distribution(detections, 'organism__class_name__name')
        self.organisms_by_genus = self._calculate_taxonomy_distribution(detections, 'organism__genus__name')
        
        self.save()
    
    def _calculate_taxonomy_distribution(self, detections, field):
        """Helper method to calculate taxonomy distribution"""
        from django.db.models import Count
        distribution = {}
        counts = detections.values(field).annotate(count=Count('id')).order_by('-count')
        for item in counts:
            if item[field]:
                distribution[item[field]] = item['count']
        return distribution
