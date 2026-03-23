from django.urls import path
from .views import NumberingView

urlpatterns = [
    path('next/', NumberingView.as_view(), name='next_number'),
]