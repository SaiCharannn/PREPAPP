from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import NumberingSequence

class NumberingView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        module = request.query_params.get('module', 'course')
        
        try:
            sequence = NumberingSequence.objects.get(module_name=module)
            sequence.current_number += 1
            sequence.save()
            
            next_number = f"{sequence.prefix}{str(sequence.current_number).zfill(sequence.padding)}"
            
            return Response({
                'nextNumber': next_number,
                'module': module
            })
        except NumberingSequence.DoesNotExist:
            return Response(
                {'error': 'Module not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )