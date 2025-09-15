from django.urls import path
from . import views

# URL patterns for detection app
urlpatterns = [
    # Detection session endpoints
    path('sessions/', views.DetectionSessionListView.as_view(), name='session-list'),
    path('sessions/<uuid:session_id>/', views.DetectionSessionDetailView.as_view(), name='session-detail'),
    path('sessions/<uuid:session_id>/end/', views.end_detection_session, name='session-end'),
    path('sessions/summary/', views.session_summary, name='session-summary'),
    
    # Detection result endpoints
    path('results/', views.DetectionResultListView.as_view(), name='detection-list'),
    path('results/<uuid:detection_id>/', views.DetectionResultDetailView.as_view(), name='detection-detail'),
    path('results/<uuid:detection_id>/verify/', views.verify_detection, name='detection-verify'),
    path('results/bulk-create/', views.bulk_create_detections, name='detection-bulk-create'),
    
    # Alert endpoints
    path('alerts/', views.LiveDetectionAlertListView.as_view(), name='alert-list'),
    path('alerts/<uuid:alert_id>/acknowledge/', views.acknowledge_alert, name='alert-acknowledge'),
    
    # Analytics endpoints
    path('trends/', views.detection_trends, name='detection-trends'),
]