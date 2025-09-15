from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def placeholder_view(request):
    """Placeholder view for analysis endpoints"""
    return Response({'message': 'Analysis endpoints coming soon'})
