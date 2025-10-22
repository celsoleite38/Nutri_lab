from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .utils import password_is_valid, email_html
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib import auth
import os
from django.conf import settings
from .models import Ativacao, PerfilProfissional
from hashlib import sha256
from django.contrib.auth.decorators import login_required
from .forms import PerfilProfissionalForm
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View


def cadastro(request):
    if request.method == "GET":
        if request.user.is_authenticated:
             return redirect('/')
        return render(request, 'cadastro.html')
    elif request.method == "POST":
            username = request.POST.get('usuario')
            senha = request.POST.get('senha')
            email = request.POST.get ('email')
            confirmar_senha = request.POST.get('confirmar_senha')
            if not password_is_valid(request, senha, confirmar_senha):
                return redirect ('/auth/cadastro')
            try:
                user = User.objects.create_user(username=username,
                                                email=email,
                                                password=senha,
                                                is_active=False)
                user.save()
                
                token = sha256(f"{username}{email}" .encode()).hexdigest()
                ativacao = Ativacao(token=token, user=user, email=email)
                ativacao.save()
                
                path_template = os.path.join(settings.BASE_DIR, 'autenticacao/templates/emails/cadastro_confirmado.html')
                email_html(path_template, 'Cadastro confirmado', [email,], username=username, link_ativacao=f"127.0.0.1:8000/auth/ativar_conta/{token}")
                messages.add_message(request, constants.SUCCESS, 'usuario cadastrado com sucesso')
                return redirect('/auth/logar')
            except:
                messages.add_message(request, constants.ERROR, 'Erro do sistema!!')
                return redirect('/auth/cadastro')
            
            
           
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

def ativar_conta(request, token):
    token = get_object_or_404(Ativacao, token=token)
    if token.ativo:
        messages.add_message(request, constants.WARNING, 'Esse token já foi usado')
        return redirect('/auth/logar')
    user = User.objects.get(username=token.user.username)
    user.is_active = True
    user.save()
    token.ativo = True
    token.save()
    messages.add_message(request, constants.SUCCESS, 'Conta ativa com sucesso')
    return redirect('/auth/logar')


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
                
                link_ativacao = f"https://nutri.innosoft.com.br/auth/ativar_conta/{token}/"
                
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
            # Log para diagnóstico (aparece apenas no servidor)
            print(f"Erro no reenvio de ativação para {email}: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'Erro ao reenviar email de ativação. Tente novamente.'
            })