from rest_framework import serializers
from .models import TaxonomyRank, MarineOrganism, OrganismDetectionProfile


class TaxonomyRankSerializer(serializers.ModelSerializer):
    """Serializer for taxonomy hierarchy"""
    
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = TaxonomyRank
        fields = ['id', 'name', 'level', 'parent', 'children']
    
    def get_children(self, obj):
        """Get child taxonomy ranks"""
        children = TaxonomyRank.objects.filter(parent=obj)
        return TaxonomyRankSerializer(children, many=True).data


class MarineOrganismListSerializer(serializers.ModelSerializer):
    """Simplified serializer for organism lists"""
    
    kingdom_name = serializers.CharField(source='kingdom.name', read_only=True)
    genus_name = serializers.CharField(source='genus.name', read_only=True)
    species_name = serializers.CharField(source='species.name', read_only=True)
    size_range = serializers.ReadOnlyField()
    
    class Meta:
        model = MarineOrganism
        fields = [
            'id', 'scientific_name', 'common_name', 'kingdom_name', 
            'genus_name', 'species_name', 'size_range', 'is_harmful',
            'toxicity_level', 'trophic_level', 'reference_image'
        ]


class MarineOrganismDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual organisms"""
    
    full_taxonomy = serializers.ReadOnlyField()
    size_range = serializers.ReadOnlyField()
    detection_profile = serializers.SerializerMethodField()
    
    # Taxonomy fields with names
    kingdom_name = serializers.CharField(source='kingdom.name', read_only=True)
    phylum_name = serializers.CharField(source='phylum.name', read_only=True)
    class_name_str = serializers.CharField(source='class_name.name', read_only=True)
    order_name = serializers.CharField(source='order.name', read_only=True)
    family_name = serializers.CharField(source='family.name', read_only=True)
    genus_name = serializers.CharField(source='genus.name', read_only=True)
    species_name = serializers.CharField(source='species.name', read_only=True)
    
    class Meta:
        model = MarineOrganism
        fields = '__all__'
        extra_fields = [
            'full_taxonomy', 'size_range', 'detection_profile',
            'kingdom_name', 'phylum_name', 'class_name_str', 'order_name',
            'family_name', 'genus_name', 'species_name'
        ]
    
    def get_detection_profile(self, obj):
        """Get detection profile if exists"""
        try:
            profile = obj.detection_profile
            return {
                'confidence_threshold': profile.model_confidence_threshold,
                'total_detections': profile.total_detections,
                'accuracy_rate': profile.accuracy_rate,
                'last_detection': profile.last_detection
            }
        except OrganismDetectionProfile.DoesNotExist:
            return None


class OrganismDetectionProfileSerializer(serializers.ModelSerializer):
    """Serializer for ML detection profiles"""
    
    organism_name = serializers.CharField(source='organism.scientific_name', read_only=True)
    accuracy_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = OrganismDetectionProfile
        fields = '__all__'
        extra_fields = ['organism_name', 'accuracy_rate']


class OrganismCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating organisms"""
    
    class Meta:
        model = MarineOrganism
        exclude = ['created_at', 'updated_at']
    
    def validate(self, data):
        """Validate size ranges and environmental parameters"""
        if data.get('typical_size_min') and data.get('typical_size_max'):
            if data['typical_size_min'] >= data['typical_size_max']:
                raise serializers.ValidationError(
                    "Minimum size must be less than maximum size"
                )
        
        if data.get('optimal_temperature_min') and data.get('optimal_temperature_max'):
            if data['optimal_temperature_min'] >= data['optimal_temperature_max']:
                raise serializers.ValidationError(
                    "Minimum temperature must be less than maximum temperature"
                )
        
        return data


class OrganismSearchSerializer(serializers.Serializer):
    """Serializer for organism search parameters"""
    
    query = serializers.CharField(required=False, help_text="Search term for name or description")
    kingdom = serializers.CharField(required=False)
    phylum = serializers.CharField(required=False)
    class_name = serializers.CharField(required=False)
    genus = serializers.CharField(required=False)
    is_harmful = serializers.BooleanField(required=False)
    toxicity_level = serializers.ChoiceField(
        choices=['none', 'low', 'moderate', 'high', 'extreme'],
        required=False
    )
    trophic_level = serializers.ChoiceField(
        choices=['primary_producer', 'primary_consumer', 'secondary_consumer', 'decomposer'],
        required=False
    )
    min_size = serializers.FloatField(required=False, help_text="Minimum size in micrometers")
    max_size = serializers.FloatField(required=False, help_text="Maximum size in micrometers")
    temperature_range = serializers.CharField(required=False, help_text="Temperature range filter")
    salinity_range = serializers.CharField(required=False, help_text="Salinity range filter")