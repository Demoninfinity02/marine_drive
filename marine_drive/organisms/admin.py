from django.contrib import admin
from .models import TaxonomyRank, MarineOrganism, OrganismDetectionProfile


@admin.register(TaxonomyRank)
class TaxonomyRankAdmin(admin.ModelAdmin):
    list_display = ['name', 'level', 'parent']
    list_filter = ['level']
    search_fields = ['name']
    ordering = ['level', 'name']


@admin.register(MarineOrganism)
class MarineOrganismAdmin(admin.ModelAdmin):
    list_display = [
        'scientific_name', 'common_name', 'kingdom', 'genus', 'species',
        'is_harmful', 'toxicity_level', 'trophic_level', 'is_active'
    ]
    list_filter = [
        'kingdom', 'phylum', 'class_name', 'is_harmful', 
        'toxicity_level', 'trophic_level', 'is_active'
    ]
    search_fields = ['scientific_name', 'common_name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('scientific_name', 'common_name', 'description', 'is_active')
        }),
        ('Taxonomy', {
            'fields': ('kingdom', 'phylum', 'class_name', 'order', 'family', 'genus', 'species')
        }),
        ('Physical Characteristics', {
            'fields': ('typical_size_min', 'typical_size_max', 'reference_image')
        }),
        ('Environmental Preferences', {
            'fields': (
                'optimal_temperature_min', 'optimal_temperature_max',
                'salinity_tolerance_min', 'salinity_tolerance_max'
            )
        }),
        ('Ecological Information', {
            'fields': ('trophic_level', 'carbon_sequestration_importance')
        }),
        ('Health & Safety', {
            'fields': ('is_harmful', 'toxicity_level')
        }),
        ('ML Model Notes', {
            'fields': ('identification_notes',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(OrganismDetectionProfile)
class OrganismDetectionProfileAdmin(admin.ModelAdmin):
    list_display = [
        'organism', 'model_confidence_threshold', 'total_detections',
        'successful_identifications', 'accuracy_rate', 'last_detection'
    ]
    list_filter = ['model_confidence_threshold']
    search_fields = ['organism__scientific_name', 'organism__common_name']
    readonly_fields = [
        'total_detections', 'successful_identifications', 'false_positives',
        'last_detection', 'accuracy_rate', 'created_at', 'updated_at'
    ]
