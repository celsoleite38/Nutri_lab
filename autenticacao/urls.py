from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import ReenviarAtivacaoView

urlpatterns = [
    path('cadastro/' , views.cadastro, name="cadastro"),
    path('logar/' , views.logar, name="logar"),
    path('sair/', views.sair, name="sair"),
    path('ativar_conta/<str:token>/', views.ativar_conta, name="ativar_conta"),
    path('recuperar-senha/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('recuperar-senha/enviado/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('recuperar-senha/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('recuperar-senha/concluido/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    path('perfil/', views.editar_perfil_profissional, name='editar_perfil'),
    path('reenviar-ativacao/', ReenviarAtivacaoView.as_view(), name='reenviar_ativacao'),
]