from .models import PerfilProfissional

def perfil_profissional(request):
    if request.user.is_authenticated:
        try:
            perfil = PerfilProfissional.objects.get(usuario=request.user)
            return {'perfil_profissional': perfil, 'perfil': perfil}
        except PerfilProfissional.DoesNotExist:
            pass
    return {'perfil_profissional': None, 'perfil': None}