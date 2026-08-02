from .models import Assinatura
from django.db.models import Q
from django.utils import timezone

def banner_assinatura(request):
    if request.user.is_authenticated:
        assinatura_ativa = Assinatura.objects.filter(
            Q(usuario=request.user) | Q(email=request.user.email),
            status__in=["ativo", "teste"],
            validade__gt=timezone.now()
        ).first()
        return {'assinatura_ativa': assinatura_ativa}
    return {'assinatura_ativa': None}