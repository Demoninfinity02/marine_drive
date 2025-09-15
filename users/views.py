from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def placeholder_view(request):
    """Placeholder view for user endpoints"""
    return Response({'message': 'User endpoints coming soon'})
