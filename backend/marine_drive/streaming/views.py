from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def placeholder_view(request):
    """Placeholder view for streaming endpoints"""
    return Response({'message': 'Streaming endpoints coming soon'})
