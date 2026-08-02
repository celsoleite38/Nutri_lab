# nutri_lab/paginas_vendas/middleware.py

from django.shortcuts import redirect
from django.utils import timezone
from .models import Assinatura
from django.db.models import Q

from django.contrib import messages
from django.contrib.messages import constants

class BloqueioAssinaturaExpiradaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Se o usuário não está logado, deixa navegar pelas páginas públicas
        if not request.user.is_authenticated:
            return self.get_response(request)

        # 2. Evita bloquear o superusuário ou membros da equipe (você trabalhando no sistema)
        if request.user.is_superuser or request.user.is_staff:
            return self.get_response(request)

        # 3. Lista de caminhos/URLs permitidas
        urls_permitidas = [
            '/vendas/',         # Página de planos, checkout, teste-grátis
            '/auth/',           # URLs de login/logout
            '/static/',         # CSS/JS da página de planos
            '/media/',          # Imagens
        ]

        # Verifica se a URL atual é uma das permitidas
        if any(request.path.startswith(url) for url in urls_permitidas):
            return self.get_response(request)

        # 4. Busca a assinatura válida mais recente deste usuário logado
        assinatura_valida = Assinatura.objects.filter(
            Q(usuario=request.user) | Q(email=request.user.email),
            status__in=["ativo", "teste"],
            validade__gt=timezone.now()
        ).exists()

        # 5. Se NÃO possui nenhuma assinatura ativa/dentro do prazo, barra o acesso
        if not assinatura_valida:
            messages.add_message(request, constants.WARNING, 'Sua assinatura expirou ou está inativa. Por favor, renove-a.')
            return redirect('pagina_vendas')

        return self.get_response(request)