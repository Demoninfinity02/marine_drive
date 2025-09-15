from django.db import models
from django.contrib.auth.models import User
from detection.models import DetectionSession, DetectionResult
from organisms.models import MarineOrganism
import uuid


class AnalysisReport(models.Model):
    """Comprehensive analysis reports for detection sessions or time periods"""
    
    REPORT_TYPES = [
        ('session', 'Single Session Analysis'),
        ('comparative', 'Comparative Analysis'),
        ('temporal', 'Temporal Trend Analysis'),
        ('biodiversity', 'Biodiversity Assessment'),
        ('environmental', 'Environmental Impact Analysis'),
        ('health_safety', 'Health & Safety Report'),
    ]
    
    report_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    
    # Report scope
    sessions = models.ManyToManyField(DetectionSession, related_name='analysis_reports')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location_filter = models.CharField(max_length=200, blank=True)
    
    # Report metadata
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_reports')
    generated_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=False)
    
    # Report content
    executive_summary = models.TextField()
    methodology = models.TextField()
    key_findings = models.JSONField(default=dict)
    recommendations = models.TextField(blank=True)
    
    # Statistical results
    total_organisms_analyzed = models.IntegerField(default=0)
    species_diversity_count = models.IntegerField(default=0)
    biodiversity_indices = models.JSONField(default=dict)
    environmental_correlations = models.JSONField(default=dict)
    
    # Health and safety analysis
    harmful_species_detected = models.JSONField(default=list)
    risk_assessment = models.TextField(blank=True)
    alert_summary = models.JSONField(default=dict)
    
    # Files and exports
    report_pdf = models.FileField(upload_to='reports/pdf/', null=True, blank=True)
    data_export_csv = models.FileField(upload_to='reports/csv/', null=True, blank=True)
    visualization_images = models.JSONField(default=list)
    
    class Meta:
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['generated_by', '-generated_at']),
            models.Index(fields=['report_type']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.generated_at.strftime('%Y-%m-%d')})"


class BiodiversityAnalysis(models.Model):
    """Detailed biodiversity analysis for specific sessions or regions"""
    
    analysis_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    report = models.ForeignKey(AnalysisReport, on_delete=models.CASCADE, related_name='biodiversity_analyses')
    
    # Diversity indices
    shannon_diversity_index = models.FloatField(null=True, blank=True)
    simpson_diversity_index = models.FloatField(null=True, blank=True)
    evenness_index = models.FloatField(null=True, blank=True)
    richness_index = models.FloatField(null=True, blank=True)
    
    # Species composition
    dominant_species = models.JSONField(default=list)
    rare_species = models.JSONField(default=list)
    endemic_species = models.JSONField(default=list)
    invasive_species = models.JSONField(default=list)
    
    # Trophic structure
    primary_producers_count = models.IntegerField(default=0)
    primary_consumers_count = models.IntegerField(default=0)
    secondary_consumers_count = models.IntegerField(default=0)
    decomposers_count = models.IntegerField(default=0)
    
    # Functional groups
    functional_group_distribution = models.JSONField(default=dict)
    trophic_pyramid_data = models.JSONField(default=dict)
    
    # Ecological indicators
    ecosystem_health_score = models.FloatField(null=True, blank=True, help_text="Score 0-100")
    pollution_indicator_species = models.JSONField(default=list)
    climate_indicator_species = models.JSONField(default=list)
    
    # Carbon cycle analysis
    carbon_fixation_potential = models.FloatField(null=True, blank=True)
    carbon_sequestration_organisms = models.JSONField(default=list)
    
    # Metadata
    analysis_date = models.DateTimeField(auto_now_add=True)
    confidence_level = models.FloatField(default=95.0, help_text="Statistical confidence level")
    
    def __str__(self):
        return f"Biodiversity Analysis {self.analysis_id} - Shannon: {self.shannon_diversity_index}"


class EnvironmentalCorrelation(models.Model):
    """Analysis of correlations between environmental factors and organism presence"""
    
    correlation_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    report = models.ForeignKey(AnalysisReport, on_delete=models.CASCADE, related_name='env_correlations')
    
    # Environmental parameters
    temperature_range = models.JSONField(default=dict)
    salinity_range = models.JSONField(default=dict)
    ph_range = models.JSONField(default=dict)
    oxygen_range = models.JSONField(default=dict)
    
    # Correlation coefficients (-1 to 1)
    temperature_organism_correlation = models.JSONField(default=dict)
    salinity_organism_correlation = models.JSONField(default=dict)
    ph_organism_correlation = models.JSONField(default=dict)
    oxygen_organism_correlation = models.JSONField(default=dict)
    
    # Statistical significance
    correlation_p_values = models.JSONField(default=dict)
    sample_size = models.IntegerField(default=0)
    
    # Environmental stress indicators
    stress_indicators = models.JSONField(default=list)
    optimal_conditions = models.JSONField(default=dict)
    tolerance_ranges = models.JSONField(default=dict)
    
    # Climate change indicators
    temperature_trend_analysis = models.JSONField(default=dict)
    species_migration_indicators = models.JSONField(default=list)
    
    analysis_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Environmental Correlation {self.correlation_id}"


class TrendAnalysis(models.Model):
    """Temporal trend analysis for organism populations"""
    
    trend_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    report = models.ForeignKey(AnalysisReport, on_delete=models.CASCADE, related_name='trend_analyses')
    organism = models.ForeignKey(MarineOrganism, on_delete=models.CASCADE, related_name='trend_analyses')
    
    # Time series data
    time_series_data = models.JSONField(default=dict, help_text="Timestamp: count pairs")
    trend_direction = models.CharField(max_length=20, choices=[
        ('increasing', 'Increasing'),
        ('decreasing', 'Decreasing'),
        ('stable', 'Stable'),
        ('fluctuating', 'Fluctuating'),
        ('seasonal', 'Seasonal Pattern'),
    ])
    
    # Statistical measures
    trend_slope = models.FloatField(null=True, blank=True)
    r_squared = models.FloatField(null=True, blank=True)
    p_value = models.FloatField(null=True, blank=True)
    confidence_interval = models.JSONField(default=dict)
    
    # Seasonality analysis
    seasonal_patterns = models.JSONField(default=dict)
    peak_months = models.JSONField(default=list)
    low_months = models.JSONField(default=list)
    
    # Forecasting
    forecast_data = models.JSONField(default=dict)
    forecast_confidence = models.FloatField(null=True, blank=True)
    
    # Anomaly detection
    anomalies_detected = models.JSONField(default=list)
    anomaly_thresholds = models.JSONField(default=dict)
    
    # Ecological implications
    population_stability = models.CharField(max_length=20, choices=[
        ('stable', 'Stable'),
        ('at_risk', 'At Risk'),
        ('declining', 'Declining'),
        ('recovering', 'Recovering'),
        ('blooming', 'Blooming'),
    ], blank=True)
    
    ecological_impact_assessment = models.TextField(blank=True)
    
    analysis_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['report', 'organism']
    
    def __str__(self):
        return f"Trend Analysis: {self.organism.scientific_name} - {self.trend_direction}"


class ComparativeAnalysis(models.Model):
    """Comparative analysis between different sessions, locations, or time periods"""
    
    comparison_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    report = models.ForeignKey(AnalysisReport, on_delete=models.CASCADE, related_name='comparative_analyses')
    
    # Comparison metadata
    comparison_type = models.CharField(max_length=20, choices=[
        ('location', 'Location Comparison'),
        ('temporal', 'Time Period Comparison'),
        ('seasonal', 'Seasonal Comparison'),
        ('treatment', 'Treatment Comparison'),
    ])
    
    # Groups being compared
    group_definitions = models.JSONField(default=dict)
    sample_sizes = models.JSONField(default=dict)
    
    # Statistical comparisons
    species_richness_comparison = models.JSONField(default=dict)
    abundance_comparison = models.JSONField(default=dict)
    diversity_indices_comparison = models.JSONField(default=dict)
    
    # Statistical tests results
    anova_results = models.JSONField(default=dict)
    t_test_results = models.JSONField(default=dict)
    chi_square_results = models.JSONField(default=dict)
    
    # Similarity measures
    jaccard_similarity = models.JSONField(default=dict)
    bray_curtis_similarity = models.JSONField(default=dict)
    
    # Key differences
    significant_differences = models.JSONField(default=list)
    effect_sizes = models.JSONField(default=dict)
    
    # Ecological interpretations
    ecological_significance = models.TextField(blank=True)
    management_implications = models.TextField(blank=True)
    
    analysis_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Comparative Analysis {self.comparison_id} - {self.comparison_type}"


class DataExport(models.Model):
    """Data export requests and generated files"""
    
    EXPORT_FORMATS = [
        ('csv', 'CSV'),
        ('excel', 'Excel'),
        ('json', 'JSON'),
        ('pdf', 'PDF Report'),
    ]
    
    export_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='data_exports')
    
    # Export parameters
    export_format = models.CharField(max_length=10, choices=EXPORT_FORMATS)
    sessions = models.ManyToManyField(DetectionSession, related_name='data_exports')
    date_range_start = models.DateTimeField()
    date_range_end = models.DateTimeField()
    
    # Data filters
    organism_filters = models.JSONField(default=dict)
    location_filters = models.JSONField(default=dict)
    confidence_threshold = models.FloatField(default=0.0)
    
    # Export options
    include_images = models.BooleanField(default=False)
    include_environmental_data = models.BooleanField(default=True)
    include_statistics = models.BooleanField(default=True)
    include_taxonomy = models.BooleanField(default=True)
    
    # Generated files
    export_file = models.FileField(upload_to='exports/', null=True, blank=True)
    file_size_mb = models.FloatField(null=True, blank=True)
    
    # Status and metadata
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='pending')
    
    requested_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # Usage tracking
    download_count = models.IntegerField(default=0)
    last_downloaded = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"Export {self.export_id} - {self.export_format.upper()} ({self.status})"
