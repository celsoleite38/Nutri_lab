# alimentos/management/commands/importar_tbca.py (ATUALIZADO)
import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from alimentos.models import Alimento, CategoriaAlimento

class Command(BaseCommand):
    help = 'Importa dados da Tabela Brasileira de Composição de Alimentos'
    
    def handle(self, *args, **options):
        self.stdout.write('Iniciando importação de dados nutricionais...')
        
        # Primeiro cria as categorias
        categorias_dict = self.criar_categorias()
        
        # Tenta importar de diferentes fontes
        csv_paths = [
            os.path.join(settings.BASE_DIR, 'alimentos', 'data', 'taco_completo.csv'),
            os.path.join(settings.BASE_DIR, 'alimentos', 'data', 'tbca_completo.csv'),
            os.path.join(settings.BASE_DIR, 'alimentos', 'data', 'alimentos.csv'),
        ]
        
        for csv_path in csv_paths:
            if os.path.exists(csv_path):
                self.importar_csv(csv_path, categorias_dict)
                return
        
        # Se nenhum CSV existir, cria dados de exemplo
        self.stdout.write(self.style.WARNING('Nenhum arquivo CSV encontrado. Criando dados de exemplo...'))
        self.criar_dados_exemplo(categorias_dict)
    
    def criar_categorias(self):
        """Cria as categorias básicas"""
        categorias = {
            'Cereais e derivados': 'Cereais, farinhas, pães, massas',
            'Verduras, hortaliças e derivados': 'Verduras, legumes e hortaliças',
            'Frutas e derivados': 'Frutas frescas e processadas',
            'Gorduras e óleos': 'Óleos vegetais, manteiga, margarina',
            'Pescados e frutos do mar': 'Peixes, camarão, mariscos',
            'Carnes e derivados': 'Carnes bovina, suína, aves',
            'Leite e derivados': 'Leite, queijos, iogurtes',
            'Bebidas': 'Sucos, refrigerantes, bebidas alcoólicas',
            'Ovos e derivados': 'Ovos e produtos à base de ovo',
            'Produtos açucarados': 'Açúcares, mel, chocolates',
            'Miscelâneas': 'Outros alimentos diversos',
            'Leguminosas e derivados': 'Feijão, lentilha, soja',
            'Nozes e sementes': 'Castanhas, amêndoas, sementes',
        }
        
        categorias_dict = {}
        for nome, desc in categorias.items():
            categoria, created = CategoriaAlimento.objects.get_or_create(
                nome=nome, 
                defaults={'descricao': desc}
            )
            categorias_dict[nome] = categoria
            if created:
                self.stdout.write(self.style.SUCCESS(f'Categoria criada: {nome}'))
        
        return categorias_dict
    
    def importar_csv(self, csv_path, categorias_dict):
        """Importa dados de um arquivo CSV"""
        self.stdout.write(f'Importando dados de: {csv_path}')
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                alimentos_importados = 0
                alimentos_atualizados = 0
                
                for row in reader:
                    try:
                        resultado = self.processar_linha_csv(row, categorias_dict)
                        if resultado == 'criado':
                            alimentos_importados += 1
                        elif resultado == 'atualizado':
                            alimentos_atualizados += 1
                            
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Erro ao processar linha: {e}'))
                
                self.stdout.write(self.style.SUCCESS(
                    f'Importação concluída! {alimentos_importados} novos, {alimentos_atualizados} atualizados'
                ))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao ler CSV: {e}'))
            self.criar_dados_exemplo(categorias_dict)
    
    def processar_linha_csv(self, row, categorias_dict):
        """Processa uma linha do CSV"""
        # Limpa e valida os dados
        def clean_value(value, default=0):
            if not value or str(value).strip() == '':
                return default
            try:
                return float(str(value).replace(',', '.'))
            except ValueError:
                return default
        
        categoria_nome = row.get('categoria', 'Miscelâneas')
        categoria = categorias_dict.get(categoria_nome)
        
        alimento, created = Alimento.objects.update_or_create(
            nome=row['nome'].strip(),
            defaults={
                'nome_cientifico': row.get('nome_cientifico', '').strip(),
                'categoria': categoria,
                'energia_kcal': clean_value(row.get('energia_kcal', 0)),
                'proteina_g': clean_value(row.get('proteina_g', 0)),
                'lipidios_g': clean_value(row.get('lipidios_g', 0)),
                'carboidrato_g': clean_value(row.get('carboidrato_g', 0)),
                'fibra_alimentar_g': clean_value(row.get('fibra_alimentar_g', 0)),
                'calcio_mg': clean_value(row.get('calcio_mg', 0)),
                'ferro_mg': clean_value(row.get('ferro_mg', 0)),
                'sodio_mg': clean_value(row.get('sodio_mg', 0)),
                'vitamina_c_mg': clean_value(row.get('vitamina_c_mg', 0)),
                'medida_caseira': row.get('medida_caseira', '').strip(),
                'quantidade_medida_caseira': clean_value(row.get('quantidade_medida_caseira', 0)),
                'fonte': row.get('fonte', 'TACO/TBCA'),
                'ativo': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ {row["nome"]}'))
            return 'criado'
        else:
            self.stdout.write(self.style.WARNING(f'↻ {row["nome"]} (atualizado)'))
            return 'atualizado'
    
    def criar_dados_exemplo(self, categorias_dict):
        """Cria dados de exemplo se não houver CSV"""
        alimentos_exemplo = [
            # ... (seus dados de exemplo anteriores)
        ]
        
        for alimento_data in alimentos_exemplo:
            try:
                categoria = categorias_dict.get(alimento_data['categoria'])
                Alimento.objects.get_or_create(
                    nome=alimento_data['nome'],
                    defaults={**alimento_data, 'categoria': categoria}
                )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Erro ao criar exemplo: {e}'))