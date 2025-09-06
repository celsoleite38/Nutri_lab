from django.shortcuts import render, redirect, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.messages import constants

from autenticacao.models import PerfilProfissional
from .models import Pacientes, DadosPaciente, Refeicao, PlanoAlimentar, ItemRefeicao
from datetime import date, datetime

from django.views.decorators.csrf import csrf_exempt
from alimentos.models import Alimento
from decimal import Decimal, InvalidOperation



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
    
    # Verificar se o paciente pertence ao nutricionista logado
    if not paciente.nutri == request.user:
        messages.add_message(request, constants.ERROR, 'Esse paciente não é seu')
        return redirect('/pacientes/')
   
    if request.method == "GET":
        dados_paciente = DadosPaciente.objects.filter(paciente=paciente).order_by('-data')
        return render(request, 'dados_paciente.html', {
            'paciente': paciente, 
            'dados_paciente': dados_paciente
        })
    
    elif request.method == "POST":
        try:
            # Função para converter e validar valores decimais
            def parse_decimal(value, default='0'):
                if not value or value.strip() == '':
                    return Decimal(default)
                # Substituir vírgula por ponto para formato decimal
                value = value.replace(',', '.')
                try:
                    return Decimal(value)
                except InvalidOperation:
                    return Decimal(default)
            
            # Converter todos os valores decimais
            peso = parse_decimal(request.POST.get('peso'))
            altura = parse_decimal(request.POST.get('altura'))
            gordura = parse_decimal(request.POST.get('gordura'))
            musculo = parse_decimal(request.POST.get('musculo'))
            hdl = parse_decimal(request.POST.get('hdl'))
            ldl = parse_decimal(request.POST.get('ldl'))
            colesterol_total = parse_decimal(request.POST.get('ctotal'))
            trigliceridios = parse_decimal(request.POST.get('trigliceridios'))
            
            # Criar instância de DadosPaciente (não sobrescrever a variável paciente)
            dados_paciente = DadosPaciente(
                paciente=paciente,
                data=datetime.now(),
                peso=peso,
                altura=altura,
                percentual_gordura=gordura,
                percentual_musculo=musculo,
                colesterol_hdl=hdl,
                colesterol_ldl=ldl,
                colesterol_total=colesterol_total,
                trigliceridios=trigliceridios
            )
            
            dados_paciente.save()
            
            messages.add_message(request, constants.SUCCESS, 'Dados cadastrados com sucesso')
            return redirect(f'/dados_paciente/{id}/')
            
        except Exception as e:
            messages.add_message(request, constants.ERROR, f'Erro ao salvar dados: {str(e)}')
            return redirect(f'/dados_paciente/{id}/')



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

@login_required(login_url='/auth/logar/')
def plano_alimentar_listar(request):
    if request.method == "GET":
        pacientes = Pacientes.objects.filter(nutri=request.user)
        # Buscar também os planos alimentares existentes
        planos = PlanoAlimentar.objects.filter(paciente__nutri=request.user).order_by('-data_criacao')
        
        return render(request, 'plano_alimentar_listar.html', {
            'pacientes': pacientes,
            'planos': planos
        })
    
@login_required(login_url='/auth/logar/')
def plano_alimentar(request, id):
    paciente = get_object_or_404(Pacientes, id=id)
    if not paciente.nutri == request.user:
        messages.add_message(request, constants.ERROR, 'Esse paciente não é seu')
        return redirect('/plano_alimentar_listar/')
    
    if request.method == "GET":
        # Use o novo sistema de refeições
        refeicoes = Refeicao.objects.filter(paciente=paciente).order_by("horario")
        
        return render(request, 'plano_alimentar.html', {
            'paciente': paciente, 
            'refeicoes': refeicoes
        })
    
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

@login_required
def criar_plano_alimentar(request, paciente_id):
    paciente = get_object_or_404(Pacientes, id=paciente_id, nutri=request.user)
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        data_inicio = request.POST.get('data_inicio')
        data_fim = request.POST.get('data_fim')
        objetivo = request.POST.get('objetivo')
        
        plano = PlanoAlimentar(
            paciente=paciente,
            nome=nome,
            data_inicio=data_inicio,
            data_fim=data_fim,
            objetivo=objetivo
        )
        plano.save()
        
        messages.success(request, 'Plano alimentar criado com sucesso!')
        return redirect('detalhes_plano_alimentar', plano_id=plano.id)
    
    return render(request, 'criar_plano_alimentar.html', {'paciente': paciente})

@login_required
def detalhes_plano_alimentar(request, plano_id):
    plano = get_object_or_404(PlanoAlimentar, id=plano_id)
    if plano.paciente.nutri != request.user:
        messages.error(request, 'Acesso não autorizado.')
        return redirect('plano_alimentar_listar')
    
    # Obter todas as refeições do paciente para poder adicionar ao plano
    refeicoes_disponiveis = Refeicao.objects.filter(paciente=plano.paciente).exclude(id__in=plano.refeicoes.values_list('id', flat=True))
    
    if request.method == 'POST':
        # Adicionar refeição ao plano
        refeicao_id = request.POST.get('refeicao_id')
        if refeicao_id:
            refeicao = get_object_or_404(Refeicao, id=refeicao_id)
            plano.refeicoes.add(refeicao)
            messages.success(request, f'Refeição "{refeicao.titulo}" adicionada ao plano.')
    
    return render(request, 'detalhes_plano_alimentar.html', {
        'plano': plano,
        'refeicoes_disponiveis': refeicoes_disponiveis,
        'total_nutrientes': plano.total_nutrientes()
    })

@login_required
def adicionar_refeicao(request, paciente_id):
    paciente = get_object_or_404(Pacientes, id=paciente_id, nutri=request.user)
    
    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        titulo = request.POST.get('titulo')
        horario = request.POST.get('horario')
        observacoes = request.POST.get('observacoes', '')
        
        refeicao = Refeicao(
            paciente=paciente,
            tipo=tipo,
            titulo=titulo,
            horario=horario,
            observacoes=observacoes
        )
        refeicao.save()
        
        messages.success(request, 'Refeição criada com sucesso!')
        return redirect('editar_refeicao', refeicao_id=refeicao.id)
    
    return render(request, 'adicionar_refeicao.html', {
        'paciente': paciente,
        'tipos_refeicao': Refeicao.TIPO_CHOICES
    })

@login_required
def editar_refeicao(request, refeicao_id):
    refeicao = get_object_or_404(Refeicao, id=refeicao_id)
    if refeicao.paciente.nutri != request.user:
        messages.error(request, 'Acesso não autorizado.')
        return redirect('plano_alimentar_listar')
    
    alimentos = Alimento.objects.filter(ativo=True)
    
    if request.method == 'POST':
        # Adicionar alimento à refeição
        alimento_id = request.POST.get('alimento_id')
        quantidade = request.POST.get('quantidade', 100)
        observacoes = request.POST.get('observacoes', '')
        
        if alimento_id:
            alimento = get_object_or_404(Alimento, id=alimento_id)
            item = ItemRefeicao(
                refeicao=refeicao,
                alimento=alimento,
                quantidade_g=quantidade,
                observacoes=observacoes
            )
            item.save()
            messages.success(request, f'{alimento.nome} adicionado à refeição.')
    
    return render(request, 'editar_refeicao.html', {
        'refeicao': refeicao,
        'alimentos': alimentos,
        'itens': refeicao.itens.all(),
        'total_nutrientes': refeicao.total_nutrientes()
    })

@login_required
def remover_item_refeicao(request, item_id):
    item = get_object_or_404(ItemRefeicao, id=item_id)
    if item.refeicao.paciente.nutri != request.user:
        messages.error(request, 'Acesso não autorizado.')
        return redirect('plano_alimentar_listar')
    
    refeicao_id = item.refeicao.id
    item.delete()
    messages.success(request, 'Item removido da refeição.')
    return redirect('editar_refeicao', refeicao_id=refeicao_id)

@login_required
def buscar_alimentos_refeicao(request):
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
            'carboidratos': float(a.carboidrato_g),
            'lipidios': float(a.lipidios_g)
        } for a in alimentos]
        
        return JsonResponse(resultados, safe=False)

@login_required
def calcular_nutrientes_item(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            alimento_id = request.POST.get('alimento_id')
            quantidade = float(request.POST.get('quantidade', 100))
            
            alimento = get_object_or_404(Alimento, id=alimento_id)
            nutrientes = alimento.calcular_nutrientes_por_porcao(quantidade)
            
            return JsonResponse({
                'success': True,
                'nutrientes': nutrientes
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Requisição inválida'})


@login_required(login_url='/auth/logar/')
def desativar_plano(request, plano_id):
    plano = get_object_or_404(PlanoAlimentar, id=plano_id)
    
    # Verifica se o usuário tem permissão (nutricionista do paciente)
    if plano.paciente.nutri != request.user:
        messages.error(request, "Você não tem permissão para desativar este plano.")
        return redirect('plano_alimentar_listar')
    
    # Desativa o plano
    plano.ativo = False
    plano.save()
    
    messages.success(request, f"Plano '{plano.nome}' desativado com sucesso!")
    return redirect('detalhes_plano_alimentar', plano_id=plano.id)

@login_required(login_url='/auth/logar/')
def reativar_plano(request, plano_id):
    plano = get_object_or_404(PlanoAlimentar, id=plano_id)
    
    if plano.paciente.nutri != request.user:
        messages.error(request, "Você não tem permissão para reativar este plano.")
        return redirect('plano_alimentar_listar')
    
    # Reativa o plano
    plano.ativo = True
    plano.save()
    
    messages.success(request, f"Plano '{plano.nome}' reativado com sucesso!")
    return redirect('detalhes_plano_alimentar', plano_id=plano.id)


@login_required(login_url='/auth/logar/')
def remover_refeicao_plano(request, plano_id, refeicao_id):
    plano = get_object_or_404(PlanoAlimentar, id=plano_id)
    refeicao = get_object_or_404(Refeicao, id=refeicao_id)
    
    # Verifica permissões
    if plano.paciente.nutri != request.user or refeicao.paciente.nutri != request.user:
        messages.error(request, "Você não tem permissão para realizar esta ação.")
        return redirect('plano_alimentar_listar')
    
    # Remove a refeição do plano
    plano.refeicoes.remove(refeicao)
    
    messages.success(request, f"Refeição '{refeicao.titulo}' removida do plano.")
    return redirect('detalhes_plano_alimentar', plano_id=plano.id)

@login_required(login_url='/auth/logar/')
def adicionar_refeicao_existente(request, plano_id):
    if request.method == 'POST':
        plano = get_object_or_404(PlanoAlimentar, id=plano_id)
        refeicao_id = request.POST.get('refeicao_id')
        
        if refeicao_id:
            refeicao = get_object_or_404(Refeicao, id=refeicao_id)
            
            # Verifica permissões
            if plano.paciente.nutri != request.user or refeicao.paciente.nutri != request.user:
                messages.error(request, "Você não tem permissão para realizar esta ação.")
                return redirect('detalhes_plano_alimentar', plano_id=plano.id)
            
            # Adiciona a refeição ao plano
            plano.refeicoes.add(refeicao)
            messages.success(request, f"Refeição '{refeicao.titulo}' adicionada ao plano.")
        
        return redirect('detalhes_plano_alimentar', plano_id=plano.id)
    
@login_required(login_url='/auth/logar/')
def detalhes_paciente_planos(request, paciente_id):
    paciente = get_object_or_404(Pacientes, id=paciente_id, nutri=request.user)
    planos = PlanoAlimentar.objects.filter(paciente=paciente).order_by('-data_criacao')
    
    return render(request, 'detalhes_paciente_planos.html', {
        'paciente': paciente,
        'planos': planos
    })