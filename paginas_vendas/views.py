from datetime import timedelta
import json
import logging
import requests
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.urls import reverse
from .models import Assinatura, Plano
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────
# Helpers Asaas
# ──────────────────────────────────────────

ASAAS_HEADERS = {
    'access_token': settings.ASAAS_API_KEY,
    'Content-Type': 'application/json',
}

ASAAS_TIMEOUT = 30


def _criar_cliente_asaas(nome, email, cpf_cnpj):
    """Cria cliente no Asaas e retorna o ID."""
    url = f"{settings.ASAAS_BASE_URL}/customers"
    payload = {
        "name": nome,
        "email": email,
        "cpfCnpj": cpf_cnpj,
    }
    resp = requests.post(url, json=payload, headers=ASAAS_HEADERS, timeout=ASAAS_TIMEOUT)
    resp.raise_for_status()
    return resp.json()['id']


def _criar_ou_buscar_cliente(nome, email, cpf_cnpj, phone,
                             postal_code, address, address_number, province, city):
    url_create = f"{settings.ASAAS_BASE_URL}/customers"
    payload = {
        "name":          nome,
        "email":         email,
        "cpfCnpj":       cpf_cnpj,
        "phone":         phone,
        "postalCode":    postal_code,
        "address":       address,
        "addressNumber": address_number,
        "province":      province,
        "city":          city,
    }
    resp = requests.post(url_create, json=payload, headers=ASAAS_HEADERS, timeout=ASAAS_TIMEOUT)

    if resp.status_code == 200:
        return resp.json()['id']

    if resp.status_code == 400:
        url_busca = f"{settings.ASAAS_BASE_URL}/customers?cpfCnpj={cpf_cnpj}"
        r = requests.get(url_busca, headers=ASAAS_HEADERS, timeout=ASAAS_TIMEOUT)
        r.raise_for_status()
        data = r.json()
        if data.get('data'):
            return data['data'][0]['id']

    resp.raise_for_status()


def _criar_checkout_asaas(customer_id, valor, descricao, url_sucesso, url_cancelamento):
    url = f"{settings.ASAAS_BASE_URL}/checkouts"
    payload = {
        "billingTypes": ["PIX", "CREDIT_CARD"],
        "chargeTypes": ["DETACHED"],
        "name": descricao,
        "value": float(valor),
        "minutesToExpire": 1440,
        "customer": customer_id,
        "items": [
            {
                "name": descricao,
                "value": float(valor),
                "quantity": 1,
            }
        ],
        "callback": {
            "successUrl": url_sucesso,
            "cancelUrl": url_cancelamento,
            "autoRedirect": True,
        },
    }
    resp = requests.post(url, json=payload, headers=ASAAS_HEADERS, timeout=ASAAS_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()

    checkout_url = data.get('link') or data.get('url')
    checkout_id = data.get('id')

    return checkout_url, checkout_id


def _consultar_pagamento_asaas(payment_id):
    """Consulta o status do pagamento no Asaas para validar o webhook."""
    url = f"{settings.ASAAS_BASE_URL}/payments/{payment_id}"
    resp = requests.get(url, headers=ASAAS_HEADERS, timeout=ASAAS_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


# ──────────────────────────────────────────
# Views
# ──────────────────────────────────────────

def pagina_vendas(request):
    todos_planos = Plano.objects.filter(ativo=True)
    planos = [p for p in todos_planos if p.visivel]
    return render(request, 'paginas_vendas/pagina_vendas.html', {'planos': planos})


def teste_gratis(request):
    if request.method == 'POST':
        email_usuario = request.POST.get('email', '').strip()

        if not email_usuario:
            return render(request, 'paginas_vendas/erro.html', {
                'mensagem': 'Por favor, informe um e-mail válido.'
            })

        # REGRA 1: Bloqueia se o e-mail já usou o teste grátis histórico
        if Assinatura.objects.filter(email=email_usuario, eh_teste_gratis=True).exists():
            return render(request, 'paginas_vendas/erro.html', {
                'mensagem': 'Este e-mail já utilizou o período de teste gratuito.',
                'email': email_usuario,
                'motivo': 'teste_ja_usado'
            })

        # REGRA 2: Bloqueia se o usuário já tem cadastro no sistema
        if User.objects.filter(email=email_usuario).exists():
            return render(request, 'paginas_vendas/erro.html', {
                'mensagem': 'Este e-mail já está cadastrado no sistema.',
                'email': email_usuario,
                'mostrar_assinaturas': True,
                'motivo': 'usuario_existente'
            })

        # FLUXO DE SUCESSO PARA USUÁRIO NOVO:
        # Salva o e-mail na sessão e joga direto para o cadastro para ele criar a conta
        request.session['email_pre_cadastro'] = email_usuario
        return redirect('cadastro')

    return render(request, 'paginas_vendas/teste_gratis_form.html')


def checkout(request, plano_slug):
    plano_obj = Plano.objects.filter(slug=plano_slug, ativo=True).first()
    if not plano_obj or not plano_obj.visivel:
        return redirect('pagina_vendas')

    plano = {
        "title": plano_obj.nome,
        "price": float(plano_obj.preco),
        "dias": plano_obj.duracao_dias,
    }

    erro = None

    if request.method == 'POST':
        email_usuario  = request.POST.get('email', '').strip()
        nome           = request.POST.get('nome', '').strip()
        cpf_cnpj       = request.POST.get('cpf_cnpj', '').strip()
        phone          = request.POST.get('phone', '').strip()
        postal_code    = request.POST.get('postal_code', '').strip()
        address        = request.POST.get('address', '').strip()
        address_number = request.POST.get('address_number', '').strip()
        province       = request.POST.get('province', '').strip()
        city           = request.POST.get('city', '').strip()

        cpf_cnpj_limpo = ''.join(filter(str.isdigit, cpf_cnpj))
        phone_limpo    = ''.join(filter(str.isdigit, phone))
        postal_limpo   = ''.join(filter(str.isdigit, postal_code))

        if len(cpf_cnpj_limpo) not in (11, 14):
            erro = 'CPF deve ter 11 dígitos ou CNPJ 14 dígitos.'
        else:
            try:
                customer_id = _criar_ou_buscar_cliente(
                    nome=nome,
                    email=email_usuario,
                    cpf_cnpj=cpf_cnpj_limpo,
                    phone=phone_limpo,
                    postal_code=postal_limpo,
                    address=address,
                    address_number=address_number,
                    province=province,
                    city=city,
                )

                url_sucesso      = request.build_absolute_uri(reverse('pagina_obrigado'))
                url_cancelamento = request.build_absolute_uri(reverse('pagina_vendas'))

                checkout_url, checkout_id = _criar_checkout_asaas(
                    customer_id=customer_id,
                    valor=plano['price'],
                    descricao=plano['title'],
                    url_sucesso=url_sucesso,
                    url_cancelamento=url_cancelamento,
                )

                if not checkout_url:
                    erro = 'Não foi possível gerar o link de pagamento. Tente novamente.'
                else:
                    validade = timezone.now() + timedelta(days=plano['dias'])
                    Assinatura.objects.create(
                        email=email_usuario,
                        plano=plano['title'],
                        valor=plano['price'],
                        validade=validade,
                        status="pendente",
                        asaas_payment_id=checkout_id or '',
                    )

                    return redirect(checkout_url)   # ← redireciona para o Asaas

            except requests.exceptions.HTTPError as e:
                erro = f"Erro ao gerar cobrança: {e.response.text}"
            except Exception as e:
                import traceback
                traceback.print_exc()
                erro = f"Erro inesperado: {str(e)}"

    return render(request, 'paginas_vendas/checkout.html', {
        'plano': plano,
        'plano_slug': plano_slug,
        'erro': erro,
    })


def pagina_obrigado(request):
    return render(request, 'paginas_vendas/obrigado.html')


@csrf_exempt
def webhook_asaas(request):
    """Recebe notificações de pagamento do Asaas."""
    if request.method != 'POST':
        return JsonResponse({"error": "Método não permitido"}, status=405)

    try:
        data = json.loads(request.body)
        evento = data.get('event')
        payment = data.get('payment', {})
        pay_id = payment.get('id', '')

        logger.info(f"[WEBHOOK] evento=%s payment_id=%s", evento, pay_id)

        if evento == 'PAYMENT_CONFIRMED' and pay_id:
            # Validação: confirma no Asaas antes de ativar (evita fraude no webhook)
            try:
                dados_pagamento = _consultar_pagamento_asaas(pay_id)
                status_confirmado = dados_pagamento.get('status') == 'CONFIRMED'
            except Exception:
                logger.exception("[WEBHOOK] Falha ao validar pagamento no Asaas")
                return JsonResponse({"status": "erro_validacao"}, status=502)

            if status_confirmado:
                atualizadas = Assinatura.objects.filter(
                    asaas_payment_id=pay_id
                ).update(status='ativo')
                logger.info("[WEBHOOK] Assinaturas ativadas: %s", atualizadas)
            else:
                logger.info("[WEBHOOK] Pagamento %s ainda não confirmado (status=%s)",
                            pay_id, dados_pagamento.get('status'))
                return JsonResponse({"status": "nao_confirmado"})

        elif evento in ('PAYMENT_OVERDUE', 'PAYMENT_DELETED') and pay_id:
            Assinatura.objects.filter(
                asaas_payment_id=pay_id
            ).update(status='cancelado')
            logger.info("[WEBHOOK] Assinatura marcada como cancelada: %s", pay_id)

        return JsonResponse({"status": "ok"})

    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)
    except Exception as e:
        logger.exception("[WEBHOOK] Erro inesperado")
        return JsonResponse({"error": str(e)}, status=500)


@staff_member_required
def dashboard_assinaturas(request):
    assinaturas = Assinatura.objects.all().order_by('-data_pagamento')
    return render(request, 'paginas_vendas/dashboard.html', {'assinaturas': assinaturas})


def recursos(request):
    return render(request, 'paginas_vendas/recursos.html')
