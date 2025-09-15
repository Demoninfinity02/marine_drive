from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404

from .models import TaxonomyRank, MarineOrganism, OrganismDetectionProfile
from .serializers import (
    TaxonomyRankSerializer, MarineOrganismListSerializer,
    MarineOrganismDetailSerializer, OrganismDetectionProfileSerializer,
    OrganismCreateUpdateSerializer, OrganismSearchSerializer
)


class TaxonomyRankListView(generics.ListCreateAPIView):
    """List and create taxonomy ranks"""
    queryset = TaxonomyRank.objects.all()
    serializer_class = TaxonomyRankSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['level', 'name']
    ordering = ['level', 'name']


class TaxonomyHierarchyView(generics.ListAPIView):
    """Get complete taxonomy hierarchy"""
    serializer_class = TaxonomyRankSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """Return root level taxonomy ranks with children"""
        return TaxonomyRank.objects.filter(parent=None)


class MarineOrganismListView(generics.ListCreateAPIView):
    """List and create marine organisms"""
    queryset = MarineOrganism.objects.filter(is_active=True)
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['scientific_name', 'common_name', 'description']
    ordering_fields = ['scientific_name', 'created_at', 'typical_size_min']
    ordering = ['scientific_name']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrganismCreateUpdateSerializer
        return MarineOrganismListSerializer


class MarineOrganismDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a specific marine organism"""
    queryset = MarineOrganism.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return OrganismCreateUpdateSerializer
        return MarineOrganismDetailSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search_organisms(request):
    """Advanced organism search with multiple parameters"""
    serializer = OrganismSearchSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    queryset = MarineOrganism.objects.filter(is_active=True)
    data = serializer.validated_data
    
    # Text search
    if 'query' in data:
        query = data['query']
        queryset = queryset.filter(
            Q(scientific_name__icontains=query) |
            Q(common_name__icontains=query) |
            Q(description__icontains=query)
        )
    
    # Taxonomy filters
    taxonomy_filters = {
        'kingdom__name__iexact': data.get('kingdom'),
        'phylum__name__iexact': data.get('phylum'),
        'class_name__name__iexact': data.get('class_name'),
        'genus__name__iexact': data.get('genus'),
    }
    
    for field, value in taxonomy_filters.items():
        if value:
            queryset = queryset.filter(**{field: value})
    
    # Boolean filters
    if 'is_harmful' in data:
        queryset = queryset.filter(is_harmful=data['is_harmful'])
    
    if 'toxicity_level' in data:
        queryset = queryset.filter(toxicity_level=data['toxicity_level'])
    
    if 'trophic_level' in data:
        queryset = queryset.filter(trophic_level=data['trophic_level'])
    
    # Size filters
    if 'min_size' in data:
        queryset = queryset.filter(typical_size_max__gte=data['min_size'])
    
    if 'max_size' in data:
        queryset = queryset.filter(typical_size_min__lte=data['max_size'])
    
    # Serialize results
    serializer = MarineOrganismListSerializer(queryset, many=True)
    
    return Response({
        'count': queryset.count(),
        'results': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def organism_statistics(request):
    """Get organism database statistics"""
    stats = {
        'total_organisms': MarineOrganism.objects.filter(is_active=True).count(),
        'harmful_organisms': MarineOrganism.objects.filter(is_harmful=True, is_active=True).count(),
        'by_kingdom': list(
            MarineOrganism.objects.filter(is_active=True)
            .values('kingdom__name')
            .annotate(count=Count('id'))
            .order_by('-count')
        ),
        'by_toxicity': list(
            MarineOrganism.objects.filter(is_active=True)
            .values('toxicity_level')
            .annotate(count=Count('id'))
            .order_by('-count')
        ),
        'by_trophic_level': list(
            MarineOrganism.objects.filter(is_active=True)
            .values('trophic_level')
            .annotate(count=Count('id'))
            .order_by('-count')
        ),
        'size_distribution': {
            'microscopic': MarineOrganism.objects.filter(typical_size_max__lt=100, is_active=True).count(),
            'small': MarineOrganism.objects.filter(typical_size_max__gte=100, typical_size_max__lt=1000, is_active=True).count(),
            'medium': MarineOrganism.objects.filter(typical_size_max__gte=1000, typical_size_max__lt=10000, is_active=True).count(),
            'large': MarineOrganism.objects.filter(typical_size_max__gte=10000, is_active=True).count(),
        }
    }
    
    return Response(stats)


class OrganismDetectionProfileListView(generics.ListCreateAPIView):
    """List and create detection profiles"""
    queryset = OrganismDetectionProfile.objects.all()
    serializer_class = OrganismDetectionProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['total_detections', 'successful_identifications', 'last_detection']
    ordering = ['-total_detections']


class OrganismDetectionProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete detection profile"""
    queryset = OrganismDetectionProfile.objects.all()
    serializer_class = OrganismDetectionProfileSerializer
    permission_classes = [IsAuthenticated]


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def detection_accuracy_report(request):
    """Get detection accuracy report for all organisms"""
    profiles = OrganismDetectionProfile.objects.select_related('organism').all()
    
    report_data = []
    for profile in profiles:
        report_data.append({
            'organism_id': profile.organism.id,
            'scientific_name': profile.organism.scientific_name,
            'common_name': profile.organism.common_name,
            'total_detections': profile.total_detections,
            'successful_identifications': profile.successful_identifications,
            'false_positives': profile.false_positives,
            'accuracy_rate': profile.accuracy_rate,
            'confidence_threshold': profile.model_confidence_threshold,
            'last_detection': profile.last_detection,
        })
    
    # Sort by accuracy rate descending
    report_data.sort(key=lambda x: x['accuracy_rate'], reverse=True)
    
    return Response({
        'total_profiles': len(report_data),
        'average_accuracy': sum(item['accuracy_rate'] for item in report_data) / len(report_data) if report_data else 0,
        'profiles': report_data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_create_organisms(request):
    """Bulk create organisms from a list"""
    if not isinstance(request.data, list):
        return Response(
            {'error': 'Expected a list of organisms'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    created_organisms = []
    errors = []
    
    for i, organism_data in enumerate(request.data):
        serializer = OrganismCreateUpdateSerializer(data=organism_data)
        if serializer.is_valid():
            try:
                organism = serializer.save()
                created_organisms.append({
                    'index': i,
                    'id': organism.id,
                    'scientific_name': organism.scientific_name
                })
            except Exception as e:
                errors.append({
                    'index': i,
                    'error': str(e)
                })
        else:
            errors.append({
                'index': i,
                'validation_errors': serializer.errors
            })
    
    return Response({
        'created_count': len(created_organisms),
        'error_count': len(errors),
        'created_organisms': created_organisms,
        'errors': errors
    }, status=status.HTTP_201_CREATED if created_organisms else status.HTTP_400_BAD_REQUEST)
