# alimentos/management/commands/importar_tbca.py
import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from alimentos.models import Alimento, CategoriaAlimento

class Command(BaseCommand):
    help = 'Importa dados iniciais da Tabela Brasileira de Composição de Alimentos (TBCA)'
    
    def handle(self, *args, **options):
        # Cria categorias básicas
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
        
        # Importa dados do CSV
        csv_path = os.path.join(settings.BASE_DIR, 'alimentos', 'data', 'tbca_completo.csv')
        
        if os.path.exists(csv_path):
            self.stdout.write('Importando dados do CSV...')
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    try:
                        categoria_nome = row.get('categoria', 'Miscelâneas')
                        categoria = categorias_dict.get(categoria_nome)
                        
                        # Converte valores vazios para 0 ou string vazia
                        def parse_value(value, default=0):
                            if value is None or value == '':
                                return default
                            try:
                                return float(value)
                            except ValueError:
                                return default
                        
                        alimento, created = Alimento.objects.get_or_create(
                            nome=row['nome'],
                            defaults={
                                'nome_cientifico': row.get('nome_cientifico', ''),
                                'categoria': categoria,
                                'energia_kcal': parse_value(row.get('energia_kcal', 0)),
                                'proteina_g': parse_value(row.get('proteina_g', 0)),
                                'lipidios_g': parse_value(row.get('lipidios_g', 0)),
                                'carboidrato_g': parse_value(row.get('carboidrato_g', 0)),
                                'fibra_alimentar_g': parse_value(row.get('fibra_alimentar_g', 0)),
                                'calcio_mg': parse_value(row.get('calcio_mg', 0)),
                                'ferro_mg': parse_value(row.get('ferro_mg', 0)),
                                'sodio_mg': parse_value(row.get('sodio_mg', 0)),
                                'vitamina_c_mg': parse_value(row.get('vitamina_c_mg', 0)),
                                'medida_caseira': row.get('medida_caseira', ''),
                                'quantidade_medida_caseira': parse_value(row.get('quantidade_medida_caseira', 0)),
                                'fonte': row.get('fonte', 'TBCA - USP')
                            }
                        )
                        
                        if created:
                            self.stdout.write(self.style.SUCCESS(f'Alimento criado: {row["nome"]}'))
                        else:
                            self.stdout.write(self.style.WARNING(f'Alimento já existe: {row["nome"]}'))
                            
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Erro ao importar {row.get("nome", "desconhecido")}: {str(e)}'))
            
            self.stdout.write(self.style.SUCCESS('Importação concluída!'))
        else:
            self.stdout.write(self.style.WARNING('Arquivo CSV não encontrado. Criando apenas categorias.'))
            # Cria alguns alimentos básicos mesmo sem CSV
            self.criar_alimentos_exemplo(categorias_dict)
    
    def criar_alimentos_exemplo(self, categorias_dict):
        """Cria alguns alimentos de exemplo se o CSV não existir"""
        alimentos_exemplo = [
            {
                'nome': 'Arroz branco cozido',
                'categoria': 'Cereais e derivados',
                'energia_kcal': 130,
                'proteina_g': 2.7,
                'lipidios_g': 0.3,
                'carboidrato_g': 28.0,
                'fibra_alimentar_g': 0.5,
                'calcio_mg': 3,
                'ferro_mg': 0.3,
                'sodio_mg': 1,
                'vitamina_c_mg': 0,
                'medida_caseira': '1 colher de servir',
                'quantidade_medida_caseira': 100
            },
            {
                'nome': 'Feijão preto cozido',
                'categoria': 'Leguminosas e derivados',
                'energia_kcal': 77,
                'proteina_g': 4.5,
                'lipidios_g': 0.5,
                'carboidrato_g': 14.0,
                'fibra_alimentar_g': 8.4,
                'calcio_mg': 26,
                'ferro_mg': 1.2,
                'sodio_mg': 1,
                'vitamina_c_mg': 0,
                'medida_caseira': '1 concha',
                'quantidade_medida_caseira': 100
            },
        ]
        
        for alimento_data in alimentos_exemplo:
            try:
                categoria = categorias_dict.get(alimento_data['categoria'])
                Alimento.objects.get_or_create(
                    nome=alimento_data['nome'],
                    defaults={
                        'categoria': categoria,
                        'energia_kcal': alimento_data['energia_kcal'],
                        'proteina_g': alimento_data['proteina_g'],
                        'lipidios_g': alimento_data['lipidios_g'],
                        'carboidrato_g': alimento_data['carboidrato_g'],
                        'fibra_alimentar_g': alimento_data['fibra_alimentar_g'],
                        'calcio_mg': alimento_data['calcio_mg'],
                        'ferro_mg': alimento_data['ferro_mg'],
                        'sodio_mg': alimento_data['sodio_mg'],
                        'vitamina_c_mg': alimento_data['vitamina_c_mg'],
                        'medida_caseira': alimento_data['medida_caseira'],
                        'quantidade_medida_caseira': alimento_data['quantidade_medida_caseira'],
                        'fonte': 'TBCA - USP (Exemplo)'
                    }
                )
                self.stdout.write(self.style.SUCCESS(f'Alimento exemplo criado: {alimento_data["nome"]}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Erro ao criar alimento exemplo: {str(e)}'))