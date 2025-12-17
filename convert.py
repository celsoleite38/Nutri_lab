import os
import sys
import django
import re

# CONFIGURAR DJANGO
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nutri_lab.settings')
django.setup()

from alimentos.models import Alimento, CategoriaAlimento

def parsear_linha_corrigido(linha):
    """Parser corrigido para campos na posição certa"""
    linha = linha.strip()
    
    # Remover aspas externas
    if linha.startswith('"') and linha.endswith('"'):
        linha = linha[1:-1]
    
    # Padronizar aspas duplas internas
    linha = linha.replace('""', '"')
    
    # Dividir corretamente por vírgulas fora de aspas
    campos = []
    campo_atual = ""
    dentro_aspas = False
    
    i = 0
    while i < len(linha):
        char = linha[i]
        
        if char == '"':
            if dentro_aspas and i + 1 < len(linha) and linha[i+1] == '"':
                # Aspa dupla dentro de campo - adicionar uma aspa
                campo_atual += '"'
                i += 1  # Pular próxima aspa
            else:
                # Aspa simples - alternar estado
                dentro_aspas = not dentro_aspas
        elif char == ',' and not dentro_aspas:
            # Fim do campo
            campos.append(campo_atual)
            campo_atual = ""
        else:
            campo_atual += char
        
        i += 1
    
    # Adicionar último campo
    if campo_atual:
        campos.append(campo_atual)
    
    return campos

def importar_pasta22_campos_corretos(arquivo_csv):
    """Importação com campos na posição CORRETA"""
    print("🍎 INICIANDO IMPORTAÇÃO COM CAMPOS CORRETOS...")
    
    # Carregar categorias
    categorias_map = {}
    for cat in CategoriaAlimento.objects.all():
        categorias_map[cat.id] = cat
    print(f"📁 Categorias carregadas: {len(categorias_map)}")
    
    with open(arquivo_csv, 'r', encoding='utf-8') as file:
        linhas = file.readlines()
    
    # Pular BOM se existir
    if linhas[0].startswith('\ufeff'):
        linhas[0] = linhas[0][1:]
    
    # Primeiro, vamos limpar todos os alimentos existentes para evitar duplicatas
    print("🧹 Limpando alimentos existentes...")
    Alimento.objects.all().delete()
    
    criados = 0
    erros = 0
    total_linhas = len(linhas) - 1
    
    print(f"📄 Total de linhas para processar: {total_linhas}")
    
    for i, linha in enumerate(linhas[1:], start=2):
        try:
            if not linha.strip():
                continue
                
            # Mostrar progresso
            if i % 50 == 0:
                print(f"📊 Processando... Linha {i}/{total_linhas + 1}")
            
            # Parse corrigido
            campos = parsear_linha_corrigido(linha)
            
            # Debug para primeiras linhas
            if i <= 5:
                print(f"DEBUG Linha {i}: {len(campos)} campos")
                for j, campo in enumerate(campos[:15]):
                    print(f"  [{j}]: '{campo}'")
            
            # Verificar se temos campos suficientes
            if len(campos) < 12:
                print(f"⚠️  Linha {i}: Apenas {len(campos)} campos, pulando...")
                erros += 1
                continue
            
            # EXTRAIR CAMPOS NA POSIÇÃO CORRETA:
            # [0]=id, [1]=nome, [2]=categoria, [3]=energia_kcal, [4]=proteina_g, etc.
            
            try:
                alimento_id = int(campos[0])
                nome = campos[1]
                categoria_id = int(campos[2])  # CATEGORIA ESTÁ NA POSIÇÃO 2
            except (ValueError, IndexError) as e:
                print(f"⚠️  Linha {i}: Dados básicos inválidos - {e}")
                erros += 1
                continue
            
            # Verificar se categoria existe
            if categoria_id not in categorias_map:
                print(f"⚠️  Linha {i}: Categoria {categoria_id} não existe para '{nome}'")
                erros += 1
                continue
            
            # Dados base - CAMPOS NA POSIÇÃO CORRETA
            dados = {
                'id': alimento_id,
                'nome': nome,
                'categoria': categorias_map[categoria_id],  # CORRETO: campo [2]
                
                # CAMPOS NUTRICIONAIS NA POSIÇÃO CORRETA:
                'energia_kcal': 0.0,    # campo [3]
                'proteina_g': 0.0,      # campo [4]  
                'lipidios_g': 0.0,      # campo [5]
                'carboidrato_g': 0.0,   # campo [6]
                'fibra_alimentar_g': 0.0, # campo [7]
                'calcio_mg': 0.0,       # campo [8]
                'ferro_mg': 0.0,        # campo [9]
                'sodio_mg': 0.0,        # campo [10]
                'vitamina_c_mg': 0.0,   # campo [11]
                
                'medida_caseira': '',
                'quantidade_medida_caseira': 0.0,
                'ativo': True,
                'fonte': 'TACO'
            }
            
            # PROCESSAR CAMPOS NUTRICIONAIS NA POSIÇÃO CORRETA
            mapeamento_campos = [
                (3, 'energia_kcal'), (4, 'proteina_g'), (5, 'lipidios_g'),
                (6, 'carboidrato_g'), (7, 'fibra_alimentar_g'), (8, 'calcio_mg'),
                (9, 'ferro_mg'), (10, 'sodio_mg'), (11, 'vitamina_c_mg')
            ]
            
            for posicao, nome_campo in mapeamento_campos:
                if posicao < len(campos):
                    try:
                        valor = campos[posicao].strip('"')
                        if valor and valor != 'NA':
                            # Converter tanto ponto quanto vírgula
                            valor_limpo = valor.replace(',', '.')
                            dados[nome_campo] = float(valor_limpo)
                    except (ValueError, TypeError) as e:
                        if i <= 5:  # Debug para primeiras linhas
                            print(f"    ⚠️  Campo {nome_campo} (pos {posicao}): '{campos[posicao]}' -> erro: {e}")
            
            # Campos de texto - POSIÇÕES CORRETAS
            if len(campos) > 12 and campos[12] and campos[12] != 'NA':
                dados['medida_caseira'] = campos[12].strip('"')
            
            if len(campos) > 13 and campos[13] and campos[13] != 'NA':
                try:
                    valor = campos[13].strip('"')
                    if valor != 'NA':
                        dados['quantidade_medida_caseira'] = float(valor.replace(',', '.'))
                except (ValueError, TypeError):
                    pass
            
            if len(campos) > 15 and campos[15] and campos[15] != 'NA':
                dados['fonte'] = campos[15].strip('"')
            
            # VERIFICAÇÃO DOS DADOS (para debug)
            if i <= 5:
                print(f"  ✅ Dados processados:")
                print(f"     ID: {dados['id']}, Nome: {dados['nome']}")
                print(f"     Categoria: {dados['categoria'].id} - {dados['categoria'].nome}")
                print(f"     Energia: {dados['energia_kcal']} kcal")
                print(f"     Proteína: {dados['proteina_g']} g")
            
            # Salvar no banco
            alimento = Alimento.objects.create(**dados)
            criados += 1
            
            if criados <= 10 or criados % 50 == 0:
                print(f"✅ {criados}º CRIADO: {nome[:40]}... (Cat: {categoria_id})")
                
        except Exception as e:
            erros += 1
            if erros <= 10:
                print(f"❌ Linha {i}: {str(e)}")
            continue
    
    # RELATÓRIO FINAL
    print(f"\n{'='*50}")
    print("🎊 IMPORTAÇÃO CORRIGIDA CONCLUÍDA!")
    print(f"{'='*50}")
    print(f"📄 Total de linhas processadas: {total_linhas}")
    print(f"✅ NOVOS alimentos criados: {criados}")
    print(f"❌ ERROS: {erros}")
    
    if criados > 0:
        taxa_sucesso = (criados) / total_linhas * 100
        print(f"📊 SUCESSO: {taxa_sucesso:.1f}%")
    
    # Estatísticas
    print(f"\n📋 ESTATÍSTICAS FINAIS:")
    print(f"{'-'*30}")
    total_banco = Alimento.objects.count()
    print(f"📊 TOTAL NO BANCO: {total_banco} alimentos")
    
    for cat_id in sorted(categorias_map.keys()):
        cat = categorias_map[cat_id]
        count = Alimento.objects.filter(categoria=cat).count()
        if count > 0:
            print(f"   {cat.id:2d}. {cat.nome:<25} : {count:3d} alimentos")

if __name__ == "__main__":
    importar_pasta22_campos_corretos('Pasta22.csv')