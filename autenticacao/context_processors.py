from .models import PerfilProfissional

def perfil_profissional(request):
    if request.user.is_authenticated:
        try:
            perfil = PerfilProfissional.objects.get(usuario=request.user)
        except PerfilProfissional.DoesNotExist:
            perfil = None
        return {'perfil': perfil}
    return {}
