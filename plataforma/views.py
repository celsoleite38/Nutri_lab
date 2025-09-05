from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.messages import constants

from autenticacao.models import PerfilProfissional
from .models import Pacientes, DadosPaciente, Refeicao, Opcao
from datetime import date, datetime

from alimentos.models import Alimento

@login_required(login_url='/auth/logar/')
def pacientes(request):
    if request.method =="GET":
        pacientes = Pacientes.objects.filter(nutri=request.user)
        return render(request, 'pacientes.html' , {'pacientes' : pacientes})
    elif request.method == "POST":
        nome = request.POST.get('nome')
        cpf = request.POST.get('cpf')
        sexo = request.POST.get('sexo')
        estadocivil = request.POST.get('estadocivil')
        datanascimento = request.POST.get('datanascimento')
        naturalidade = request.POST.get('naturalidade')
        profissao = request.POST.get('profissao')
        email = request.POST.get('email')
        telefone = request.POST.get('telefone')
        endereco = request.POST.get('endereco')
        
        if (len(nome.strip()) == 0) or (len(sexo.strip()) == 0) or (len(cpf.strip()) == 0) or (len(estadocivil.strip()) == 0) or (len(datanascimento.strip()) == 0) or (len(naturalidade.strip()) == 0) or (len(profissao.strip()) == 0) or (len(email.strip()) == 0) or (len(telefone.strip()) == 0) or (len(endereco.strip()) == 0):
            messages.add_message(request, constants.ERROR, 'Preencha todos os campos')
            return redirect('/pacientes/')
            
        
    
            
        paciente = Pacientes.objects.filter(email=email)
        
        if paciente.exists():
                messages.add_message(request, constants.ERROR, 'Já existe um paciente com esse E-mail')
                return redirect('/pacientes/')
            
        try:
            p1 = Pacientes(
                nome=nome,
                cpf=cpf,
                sexo=sexo,
                estadocivil=estadocivil,
                datanascimento=datanascimento,
                naturalidade=naturalidade,
                profissao=profissao,
                email=email,
                telefone=telefone,
                endereco=endereco,
                nutri=request.user
            )
                
            p1.save()
            messages.add_message(request, constants.SUCCESS, 'Paciente cadastrado com sucesso')
            return redirect('/pacientes/')
        except:
            messages.add_message(request, constants.ERROR, 'Erro Interno')
            return redirect('/pacientes/')

@login_required(login_url='/auth/logar/')
def dados_paciente_listar(request):
    if request.method == "GET":
        pacientes = Pacientes.objects.filter(nutri=request.user)
        return render(request, 'dados_paciente_listar.html', {'pacientes': pacientes})
    
@login_required(login_url='/auth/logar/')
def dados_paciente(request, id):
        paciente = get_object_or_404(Pacientes, id=id)
        if not paciente.nutri == request.user:
            messages.add_message(request, constants.ERROR, 'Esse paciente não é seu')
            return render(request, 'dados_paciente.html', {'paciente': paciente})
   
        if request.method == "GET":
            dados_paciente = DadosPaciente.objects.filter(paciente=paciente)
            return render(request, 'dados_paciente.html', {'paciente': paciente, 'dados_paciente': dados_paciente})
        elif request.method == "POST":
            peso = request.POST.get('peso')
            altura = request.POST.get('altura')
            gordura = request.POST.get('gordura')
            musculo = request.POST.get('musculo')
            
            hdl = request.POST.get('hdl')
            ldl = request.POST.get('ldl')
            colesterol_total = request.POST.get('ctotal')
            trigliceridios = request.POST.get('trigliceridios')
            
            paciente = DadosPaciente(paciente=paciente,
                                    data=datetime.now(),
                                    peso=peso,
                                    altura=altura,
                                    percentual_gordura=gordura,
                                    percentual_musculo=musculo,
                                    colesterol_hdl=hdl,
                                    colesterol_ldl=ldl,
                                    colesterol_total=colesterol_total,
                                    trigliceridios=trigliceridios)
            paciente.save()
            
            messages.add_message(request, constants.SUCCESS, 'Dados cadastrado com sucesso')
            return redirect('/dados_paciente/')
from django.views.decorators.csrf import csrf_exempt
@login_required(login_url='/auth/logar/')
@csrf_exempt
def grafico_peso(request, id):
    paciente = Pacientes.objects.get(id=id)
    dados = DadosPaciente.objects.filter(paciente=paciente).order_by("data")
    pesos = [dado.peso for dado in dados]
    labels = list(range(len(pesos)))
    data = {'peso': pesos,
            'labels': labels}
    return JsonResponse(data)

def plano_alimentar_listar(request):
    if request.method == "GET":
        pacientes = Pacientes.objects.filter(nutri=request.user)
        return render(request, 'plano_alimentar_listar.html', {'pacientes': pacientes})
    
def plano_alimentar(request, id):
    paciente = get_object_or_404(Pacientes, id=id)
    if not paciente.nutri == request.user:
        messages.add_message(request, constants.ERROR, 'Esse paciente não é seu')
        return redirect('/plano_alimentar_listar/')
    
    if request.method == "GET":
        r1 = Refeicao.objects.filter(paciente=paciente).order_by("horario")
        opcao = Opcao.objects.all()
        return render(request, 'plano_alimentar.html', {'paciente': paciente, 'refeicao': r1, 'opcao':opcao})
    
def refeicao(request, id_paciente):
    paciente = get_object_or_404(Pacientes, id=id_paciente)
    if not paciente.nutri == request.user:
        messages.add_message(request, constants.ERROR, 'Esse paciente não é seu')
        return redirect('/dados_paciente/')
    
    if request.method == "POST":
        titulo = request.POST.get('titulo')
        horario = request.POST.get('horario')
        carboidratos = request.POST.get('carboidratos')
        proteinas = request.POST.get('proteinas')
        gorduras = request.POST.get('gorduras')
        
        r1 = Refeicao(paciente=paciente,
                        titulo=titulo,
                        horario=horario,
                        carboidratos=carboidratos,
                        proteinas=proteinas,
                        gorduras=gorduras)
        
        r1.save()
        
        messages.add_message(request, constants.SUCCESS, 'Refeição cadastrada')
        return redirect(f'/plano_alimentar/{id_paciente}')

def opcao(request, id_paciente):
    if request.method == "POST":
        id_refeicao = request.POST.get('refeicao')
        imagem = request.FILES.get('imagem')
        descricao = request.POST.get('descricao')
        
        o1 = Opcao(refeicao_id=id_refeicao,
                    imagem=imagem,
                    descricao=descricao)
        
        o1.save()
        messages.add_message(request, constants.SUCCESS, 'Opção cadastrada')
        return redirect(f'/plano_alimentar/{id_paciente}')
    
@login_required(login_url='/auth/logar/')
def imprimir_dados_paciente(request, id):
    paciente = get_object_or_404(Pacientes, id=id)
    dados_paciente = DadosPaciente.objects.filter(paciente=paciente)
    if not paciente.nutri == request.user:
        messages.add_message(request, constants.ERROR, 'Acesso negado a este PACIENTE. ')
        return redirect('/dados_paciente/')
    if request.method == 'POST':
        # Não há nada a fazer aqui, pois não estamos lidando com formulários
        pass
    else:
        return render(request, 'imprimir_dados_paciente.html', {
            'paciente': paciente,
            'dados_paciente': dados_paciente,
            'today': date.today()
        })
    
@login_required(login_url='/auth/logar/')
def editar_paciente(request, id):
    paciente = get_object_or_404(Pacientes, id=id)
    if not paciente.nutri == request.user:
        messages.add_message(request, constants.ERROR, 'Esse paciente não é seu')
        return redirect('/pacientes/')
    if request.method == "POST":
        paciente.nome = request.POST.get('nome')
        paciente.cpf = request.POST.get('cpf')
        paciente.sexo = request.POST.get('sexo')
        paciente.estadocivil = request.POST.get('estadocivil')
        paciente.datanascimento = request.POST.get('datanascimento')
        paciente.naturalidade = request.POST.get('naturalidade')
        paciente.profissao = request.POST.get('profissao')
        paciente.email = request.POST.get('email')
        paciente.telefone = request.POST.get('telefone')
        paciente.endereco = request.POST.get('endereco')
        
        if any(len(campo.strip()) == 0 for campo in [
            paciente.nome, paciente.sexo, paciente.estadocivil, paciente.datanascimento,
            paciente.naturalidade, paciente.profissao, paciente.email, paciente.telefone,
            paciente.endereco
        ]):
            messages.add_message(request, constants.ERROR, 'Preencha todos os campos')
            return redirect(f'/editar_paciente/{id}/')

        try:
            paciente.datanascimento = datetime.strptime(paciente.datanascimento, '%Y-%m-%d').date()
            paciente.save()
            messages.add_message(request, constants.SUCCESS, 'Paciente atualizado com sucesso!')
            return redirect('/pacientes/')
        except:
            messages.add_message(request, constants.ERROR, 'Erro ao atualizar paciente')
            messages.add_message(request, constants.ERROR, 'Data de nascimento inválida')
            return redirect(f'/editar_paciente/{id}/')

    return render(request, 'editar_paciente.html', {'paciente': paciente})

def imprimir_paciente(request, id):
    paciente = get_object_or_404(Pacientes, id=id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{paciente.nome}.pdf"'

    p = canvas.Canvas(response)

    # Criando uma página para cada paciente
    p.drawString(100, 800, f"Paciente: {paciente.nome}")
    p.drawString(100, 780, f"Sexo: {paciente.sexo}")
    p.drawString(100, 760, f"Estado Civil: {paciente.estadocivil}")
    p.drawString(100, 740, f"Data de Nascimento: {paciente.datanascimento}")
    p.drawString(100, 720, f"Naturalidade: {paciente.naturalidade}")
    p.drawString(100, 700, f"Profissão: {paciente.profissao}")
    p.drawString(100, 680, f"E-mail: {paciente.email}")
    p.drawString(100, 660, f"Telefone: {paciente.telefone}")
    p.drawString(100, 640, f"Endereço: {paciente.endereco}")

    # Finaliza a página
    p.showPage()
    p.save()

    return response

def imprimir_opcao(request, paciente_id):
    paciente = get_object_or_404(Pacientes, id=paciente_id)
    opcoes = Opcao.objects.filter(refeicao__paciente=paciente)
    perfil = PerfilProfissional.objects.filter(usuario=request.user).first()

    # Sempre filtra as opções do paciente (para mostrar na seleção)
    opcoes = Opcao.objects.filter(refeicao__paciente=paciente)

    if request.method == 'POST':
        # Se enviou o formulário, gera o relatório para impressão
        ids_selecionados = request.POST.getlist('opcoes')
        opcoes_selecionadas = opcoes.filter(id__in=ids_selecionados) if ids_selecionados else opcoes

        return render(request, 'relatorio_impressao.html', {
            'paciente': paciente,
            'opcoes': opcoes_selecionadas,
            'perfil': perfil,
            'today':date.today()
        })

    # GET: Mostra a página de seleção
    return render(request, 'selecionar_opcao.html', {
        'paciente': paciente,
        'opcoes': opcoes,
        'perfil': perfil,
        'today':date.today()
        
    })

def buscar_alimentos_plano(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        termo = request.GET.get('q', '')
        alimentos = Alimento.objects.filter(
            nome__icontains=termo, 
            ativo=True
        )[:10]
        
        resultados = [{
            'id': a.id,
            'nome': a.nome,
            'categoria': a.categoria.nome if a.categoria else '',
            'medida': a.medida_caseira,
            'energia': float(a.energia_kcal),
            'proteinas': float(a.proteina_g),
            'carboidratos': float(a.carboidrato_g)
        } for a in alimentos]
        
        return JsonResponse(resultados, safe=False)
    
    
def calcular_nutrientes_plano(request, plano_id):
    plano = get_object_or_404(PlanoAlimentar, id=plano_id)
    total_nutrientes = {
        'energia': 0, 'proteinas': 0, 'carboidratos': 0, 
        'lipidios': 0, 'fibras': 0
    }
    
    for refeicao in plano.refeicoes.all():
        for item in refeicao.itens.all():
            nutrientes = item.nutrientes_totais()
            for key in total_nutrientes:
                total_nutrientes[key] += nutrientes.get(key, 0)
    
    return JsonResponse(total_nutrientes)

# plataforma/views.py


def adicionar_alimento_refeicao(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            refeicao_id = request.POST.get('refeicao_id')
            alimento_id = request.POST.get('alimento_id')
            quantidade_g = float(request.POST.get('quantidade_g', 100))
            
            # Aqui você precisaria ter o modelo Refeicao
            # refeicao = get_object_or_404(Refeicao, id=refeicao_id)
            alimento = get_object_or_404(Alimento, id=alimento_id)
            
            # Simulação - depois implemente com seu modelo real
            nutrientes = alimento.calcular_nutrientes_por_porcao(quantidade_g)
            
            return JsonResponse({
                'success': True,
                'alimento': alimento.nome,
                'quantidade': quantidade_g,
                'nutrientes': nutrientes,
                'medida_caseira': alimento.medida_caseira
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Requisição inválida'})