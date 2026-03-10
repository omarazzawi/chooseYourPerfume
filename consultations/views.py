from django.shortcuts import render
from .models import ConsultationSession


def consultation_list(request):
    """Display all available consultation sessions."""
    sessions = ConsultationSession.objects.filter(is_available=True)
    return render(request, 'consultations/consultation_list.html', {'sessions': sessions})