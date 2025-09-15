from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# URL patterns for organisms app
urlpatterns = [
    # Taxonomy endpoints
    path('taxonomy/', views.TaxonomyRankListView.as_view(), name='taxonomy-list'),
    path('taxonomy/hierarchy/', views.TaxonomyHierarchyView.as_view(), name='taxonomy-hierarchy'),
    
    # Organism endpoints
    path('', views.MarineOrganismListView.as_view(), name='organism-list'),
    path('<int:pk>/', views.MarineOrganismDetailView.as_view(), name='organism-detail'),
    path('search/', views.search_organisms, name='organism-search'),
    path('statistics/', views.organism_statistics, name='organism-statistics'),
    path('bulk-create/', views.bulk_create_organisms, name='organism-bulk-create'),
    
    # Detection profile endpoints
    path('detection-profiles/', views.OrganismDetectionProfileListView.as_view(), name='detection-profile-list'),
    path('detection-profiles/<int:pk>/', views.OrganismDetectionProfileDetailView.as_view(), name='detection-profile-detail'),
    path('detection-profiles/accuracy-report/', views.detection_accuracy_report, name='detection-accuracy-report'),
]