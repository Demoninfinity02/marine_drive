from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class TaxonomyRank(models.Model):
    """Hierarchical taxonomy classification system for marine organisms"""
    name = models.CharField(max_length=100, unique=True)
    level = models.IntegerField()  # 1=Kingdom, 2=Phylum, 3=Class, 4=Order, 5=Family, 6=Genus, 7=Species
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        ordering = ['level', 'name']
    
    def __str__(self):
        return f"{self.name} (Level {self.level})"


class MarineOrganism(models.Model):
    """Master database of marine organisms with taxonomic classification"""
    
    # Taxonomic Classification
    kingdom = models.ForeignKey(TaxonomyRank, on_delete=models.CASCADE, related_name='kingdom_organisms', null=True)
    phylum = models.ForeignKey(TaxonomyRank, on_delete=models.CASCADE, related_name='phylum_organisms', null=True)
    class_name = models.ForeignKey(TaxonomyRank, on_delete=models.CASCADE, related_name='class_organisms', null=True)
    order = models.ForeignKey(TaxonomyRank, on_delete=models.CASCADE, related_name='order_organisms', null=True)
    family = models.ForeignKey(TaxonomyRank, on_delete=models.CASCADE, related_name='family_organisms', null=True)
    genus = models.ForeignKey(TaxonomyRank, on_delete=models.CASCADE, related_name='genus_organisms', null=True)
    species = models.ForeignKey(TaxonomyRank, on_delete=models.CASCADE, related_name='species_organisms', null=True)
    
    # Common identification
    common_name = models.CharField(max_length=200, blank=True)
    scientific_name = models.CharField(max_length=200, unique=True)
    
    # Physical characteristics
    typical_size_min = models.FloatField(help_text="Minimum size in micrometers", validators=[MinValueValidator(0.1)])
    typical_size_max = models.FloatField(help_text="Maximum size in micrometers", validators=[MinValueValidator(0.1)])
    
    # Environmental preferences
    optimal_temperature_min = models.FloatField(null=True, blank=True, help_text="Minimum optimal temperature in Celsius")
    optimal_temperature_max = models.FloatField(null=True, blank=True, help_text="Maximum optimal temperature in Celsius")
    salinity_tolerance_min = models.FloatField(null=True, blank=True, help_text="Minimum salinity tolerance in PSU")
    salinity_tolerance_max = models.FloatField(null=True, blank=True, help_text="Maximum salinity tolerance in PSU")
    
    # Ecological significance
    trophic_level = models.CharField(max_length=50, choices=[
        ('primary_producer', 'Primary Producer'),
        ('primary_consumer', 'Primary Consumer'),
        ('secondary_consumer', 'Secondary Consumer'),
        ('decomposer', 'Decomposer'),
    ], blank=True)
    
    # Health and safety indicators
    is_harmful = models.BooleanField(default=False, help_text="Indicates if organism is toxic or harmful")
    toxicity_level = models.CharField(max_length=20, choices=[
        ('none', 'Non-toxic'),
        ('low', 'Low toxicity'),
        ('moderate', 'Moderate toxicity'),
        ('high', 'High toxicity'),
        ('extreme', 'Extremely toxic'),
    ], default='none')
    
    # Carbon cycle importance
    carbon_sequestration_importance = models.CharField(max_length=20, choices=[
        ('low', 'Low importance'),
        ('moderate', 'Moderate importance'),
        ('high', 'High importance'),
        ('critical', 'Critical importance'),
    ], default='low')
    
    # Reference and identification
    description = models.TextField(blank=True)
    identification_notes = models.TextField(blank=True, help_text="Key features for ML model identification")
    reference_image = models.ImageField(upload_to='organisms/references/', null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['scientific_name']
        indexes = [
            models.Index(fields=['scientific_name']),
            models.Index(fields=['common_name']),
            models.Index(fields=['is_harmful']),
            models.Index(fields=['genus', 'species']),
        ]
    
    def __str__(self):
        return f"{self.scientific_name} ({self.common_name})" if self.common_name else self.scientific_name
    
    @property
    def full_taxonomy(self):
        """Returns complete taxonomic classification"""
        return {
            'kingdom': self.kingdom.name if self.kingdom else None,
            'phylum': self.phylum.name if self.phylum else None,
            'class': self.class_name.name if self.class_name else None,
            'order': self.order.name if self.order else None,
            'family': self.family.name if self.family else None,
            'genus': self.genus.name if self.genus else None,
            'species': self.species.name if self.species else None,
        }
    
    @property
    def size_range(self):
        """Returns formatted size range"""
        return f"{self.typical_size_min}-{self.typical_size_max} μm"


class OrganismDetectionProfile(models.Model):
    """ML model detection profile for each organism"""
    organism = models.OneToOneField(MarineOrganism, on_delete=models.CASCADE, related_name='detection_profile')
    
    # ML Model parameters
    model_confidence_threshold = models.FloatField(
        default=0.7, 
        validators=[MinValueValidator(0.1), MaxValueValidator(1.0)],
        help_text="Minimum confidence score for detection"
    )
    
    # Visual characteristics for ML
    shape_descriptors = models.JSONField(default=dict, help_text="Shape features for ML model")
    color_profile = models.JSONField(default=dict, help_text="Color characteristics")
    texture_features = models.JSONField(default=dict, help_text="Texture analysis features")
    
    # Detection statistics
    total_detections = models.IntegerField(default=0)
    successful_identifications = models.IntegerField(default=0)
    false_positives = models.IntegerField(default=0)
    last_detection = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def accuracy_rate(self):
        """Calculate detection accuracy percentage"""
        if self.total_detections == 0:
            return 0
        return (self.successful_identifications / self.total_detections) * 100
    
    def __str__(self):
        return f"Detection Profile for {self.organism.scientific_name}"
