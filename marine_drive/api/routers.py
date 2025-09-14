from rest_framework.routers import DefaultRouter
from detection.views import DetectionResultViewSet
from monitoring.views import AlertViewSet
from users.views import UserViewSet

router = DefaultRouter()
router.register(r'detections', DetectionResultViewSet, basename='detection')
router.register(r'alerts', AlertViewSet, basename='alert')
router.register(r'users', UserViewSet, basename='users')
