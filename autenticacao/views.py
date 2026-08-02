from django.shortcuts import render, redirect
import logging
from django.http import HttpResponse, JsonResponse
from .utils import password_is_valid, email_html
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib import auth
import os
from django.conf import settings
from .models import Ativacao, PerfilProfissional, AlteracaoEmail
from hashlib import sha256
from django.contrib.auth.decorators import login_required
from .forms import PerfilProfissionalForm
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from paginas_vendas.models import Assinatura


def cadastro(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect('/')
        email_fixo = request.session.get('email_pre_cadastro')
        return render(request, 'cadastro.html', {'email_fixo': email_fixo})

    elif request.method == "POST":
        username = request.POST.get('usuario')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')
        email_pre_cadastro = request.session.get('email_pre_cadastro')

        if email_pre_cadastro:
            email = email_pre_cadastro

        if not password_is_valid(request, senha, confirmar_senha):
            return redirect('/auth/cadastro')

        if User.objects.filter(username=username).exists():
            messages.add_message(request, constants.ERROR, 'Este nome de usuário já está em uso.')
            return redirect('/auth/cadastro')

        if User.objects.filter(email=email).exists():
            messages.add_message(request, constants.ERROR, 'Este e-mail já está cadastrado.')
            return redirect('/auth/cadastro')

        try:
            user = User.objects.create_user(
                username=username,
                password=senha,
                email=email,
                is_active=False
            )

            if email_pre_cadastro:
                Assinatura.objects.create(
                    usuario=user,
                    email=email,
                    plano='teste_gratis',
                    valor=0,
                    validade=timezone.now() + timedelta(days=7),
                    status='teste',
                    eh_teste_gratis=True,
                )
                del request.session['email_pre_cadastro']
            else:
                # Associa assinaturas pendentes ao novo usuário
                Assinatura.objects.filter(email=email, usuario__isnull=True).update(usuario=user)

            token = sha256(f"{username}{email}".encode()).hexdigest()
            Ativacao(token=token, user=user, email=email).save() # Adicionar email ao Ativacao

        except Exception as e:
            logger.exception("Erro ao criar usuário")
            messages.add_message(request, constants.ERROR, 'Erro interno ao criar conta. Tente novamente.')
            return redirect('/auth/cadastro')

        try:
            path_template = os.path.join(settings.BASE_DIR, 'autenticacao/templates/emails/cadastro_confirmado.html')
            link_ativacao = request.build_absolute_uri(reverse('ativar_conta', args=[token]))
            email_html(path_template, 'Cadastro confirmado', [email], username=username,
                       link_ativacao=link_ativacao)
        except Exception as e:
            logger.exception("Erro ao enviar e-mail de ativação")
            messages.add_message(request, constants.WARNING,
                                  'Conta criada! Porém houve um problema ao enviar o e-mail de ativação. '
                                  'Use a opção "Reenviar ativação" na tela de login.')

        messages.add_message(request, constants.SUCCESS, 'Usuário cadastrado!')
        messages.add_message(request, constants.SUCCESS, 'Verifique seu e-mail para confirmar seu cadastro.')
        return redirect('/auth/logar/')

def ativar_conta(request, token): # Adicionar esta view
    ativacao = get_object_or_404(Ativacao, token=token)
    user = ativacao.user
    user.is_active = True
    user.save()
    ativacao.ativo = True
    ativacao.save()
    messages.add_message(request, constants.SUCCESS, 'Sua conta foi ativada com sucesso! Faça login.')
    return redirect('/auth/logar/')
            
            
           
def logar(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect('plataforma:pacientes')
        return render(request, 'logar.html')
    elif request.method == "POST":
        username = request.POST.get('usuario')
        senha = request.POST.get('senha')
        
        usuario = auth.authenticate(username=username, password=senha)
        
        if not usuario:
            messages.add_message(request, constants.ERROR, 'Username ou senha inválidos')
            return redirect('/auth/logar')
        else:
            auth.login(request, usuario)
            return redirect('/plataforma/pacientes/')
        
def sair(request):
    auth.logout(request) 
    return redirect('/auth/logar')


@login_required
def editar_perfil_profissional(request):
    perfil, _ = PerfilProfissional.objects.get_or_create(usuario=request.user)

    if request.method == 'POST':
        form = PerfilProfissionalForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            messages.add_message(request, constants.SUCCESS, 'Usuário Editado com Sucesso')
            return redirect('plataforma:pacientes')  
    else:
        form = PerfilProfissionalForm(instance=perfil)
    
    return render(request, 'editar_perfil_profissional.html', {'form': form, 'perfil': perfil}) 



@method_decorator(csrf_exempt, name='dispatch')
class ReenviarAtivacaoView(View):
    def post(self, request):
        email = request.POST.get('email')
        
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # Busca flexível por email ou username
            try:
                usuario = User.objects.get(email=email)
            except User.DoesNotExist:
                usuario = User.objects.get(username=email)
            
            if usuario.is_active:
                return JsonResponse({
                    'success': False,
                    'message': 'Esta conta já está ativa!'
                })
            else:
                # Gera novo token usando o mesmo método do cadastro
                token = sha256(f"{usuario.username}{usuario.email}".encode()).hexdigest()
                
                # Atualiza ou cria o token de ativação
                ativacao, created = Ativacao.objects.get_or_create(
                    user=usuario,
                    defaults={'token': token, 'ativo': False, 'email': usuario.email}
                )
                if not created:
                    ativacao.token = token
                    ativacao.ativo = False
                    ativacao.save()
                
                link_ativacao = request.build_absolute_uri(reverse('ativar_conta', args=[token]))
                
                # Envia o email
                path_template = os.path.join(settings.BASE_DIR, 'autenticacao/templates/emails/cadastro_confirmado.html')
                email_html(path_template, 'Cadastro confirmado', [usuario.email], 
                          username=usuario.username, link_ativacao=link_ativacao)
                
                return JsonResponse({
                    'success': True,
                    'message': 'Email de ativação reenviado com sucesso! Verifique sua caixa de entrada.'
                })
                
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Email não encontrado em nosso sistema.'
            })
        except Exception as e:
            logger.exception("Erro no reenvio de ativação para %s", email)
            return JsonResponse({
                'success': False,
                'message': 'Erro ao reenviar email de ativação. Tente novamente.'
            })
        
@login_required
def solicitar_troca_email(request):
    if request.method == "POST":
        novo_email = request.POST.get('novo_email')
        
        if User.objects.filter(email=novo_email).exists():
            messages.add_message(request, constants.ERROR, 'Este e-mail já está em uso.')
            return redirect('/auth/perfil/') # Ou a URL do seu perfil

        # Gera token único
        token = sha256(f"{request.user.username}{novo_email}{timezone.now()}".encode()).hexdigest()
        
        # Salva ou atualiza a solicitação
        AlteracaoEmail.objects.update_or_create(
            usuario=request.user,
            defaults={'novo_email': novo_email, 'token': token}
        )

        # Envia e-mail de confirmação
        try:
            path_template = os.path.join(settings.BASE_DIR, 'autenticacao/templates/emails/troca_email.html')
            email_html(
                path_template, 
                'Confirme a alteração de e-mail', 
                [novo_email], 
                username=request.user.username,
                link_confirmacao=request.build_absolute_uri(reverse('confirmar_troca_email', args=[token]))
             )
            messages.add_message(request, constants.SUCCESS, f'Enviamos um link de confirmação para {novo_email}.')
        except Exception as e:
            logger.exception("Erro ao enviar e-mail de confirmação de troca")
            messages.add_message(request, constants.ERROR, 'Erro ao enviar e-mail de confirmação.')

        return redirect('/') # Redireciona para home ou perfil
    
    return render(request, 'solicitar_troca_email.html')

def confirmar_troca_email(request, token):
    solicitacao = get_object_or_404(AlteracaoEmail, token=token)
    
    # Verifica se o token não expirou (ex: 24h)
    if solicitacao.criado_em < timezone.now() - timedelta(hours=24):
        solicitacao.delete()
        messages.add_message(request, constants.ERROR, 'Este link de confirmação expirou.')
        return redirect('/auth/logar/')

    user = solicitacao.usuario
    user.email = solicitacao.novo_email
    user.save()
    
    solicitacao.delete()
    messages.add_message(request, constants.SUCCESS, 'E-mail alterado com sucesso!')
    return redirect('/auth/logar/')