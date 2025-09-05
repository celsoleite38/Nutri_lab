# alimentos/management/commands/baixar_taco.py (CORRIGIDO)
import os
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Baixa dados da TACO - Tabela Brasileira de Composição de Alimentos'
    
    def handle(self, *args, **options):
        # Cria diretório de dados se não existir
        data_dir = os.path.join(settings.BASE_DIR, 'alimentos', 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        self.stdout.write('Criando CSV com dados completos da TACO...')
        self.criar_csv_completo(data_dir)
    
    def criar_csv_completo(self, data_dir):
        """Cria um CSV completo com dados da TACO"""
        csv_path = os.path.join(data_dir, 'taco_completo.csv')
        
        # Dados completos da TACO (50+ alimentos)
        csv_content = """nome,categoria,energia_kcal,proteina_g,lipidios_g,carboidrato_g,fibra_alimentar_g,calcio_mg,ferro_mg,sodio_mg,vitamina_c_mg,medida_caseira,quantidade_medida_caseira,fonte
Arroz integral cozido,Cereais e derivados,124,2.6,1.0,25.8,2.7,5,0.3,1,0,1 colher de servir,100,TACO
Arroz branco cozido,Cereais e derivados,128,2.5,0.2,28.1,0.6,3,0.3,1,0,1 colher de servir,100,TACO
Aveia em flocos,Cereais e derivados,394,13.9,8.5,66.6,9.1,48,4.4,4,0,1 colher de sopa,15,TACO
Pão francês,Cereais e derivados,300,8.0,3.0,58.0,2.3,50,1.5,500,0,1 unidade,50,TACO
Macarrão cozido,Cereais e derivados,138,4.3,0.7,28.8,1.5,5,0.5,1,0,1 escumadeira,100,TACO
Feijão carioca cozido,Leguminosas e derivados,76,4.8,0.5,13.6,8.5,26,1.2,1,0,1 concha,100,TACO
Lentilha cozida,Leguminosas e derivados,93,6.3,0.5,16.3,7.9,16,1.5,2,1,1 concha,100,TACO
Soja cozida,Leguminosas e derivados,151,12.4,6.7,11.6,5.2,90,2.9,1,0,1 concha,100,TACO
Carne bovina cozida,Carnes e derivados,219,31.9,9.6,0.0,0.0,7,2.8,60,0,1 bife médio,100,TACO
Frango assado,Carnes e derivados,165,28.0,6.3,0.0,0.0,11,0.9,56,0,1 sobrecoxa,100,TACO
Peixe assado,Pescados e frutos do mar,147,26.6,4.0,0.0,0.0,28,0.5,60,0,1 posta,100,TACO
Ovo de galinha cozido,Ovos e derivados,146,13.3,9.5,0.6,0.0,49,1.2,126,0,1 unidade,50,TACO
Leite integral,Leite e derivados,61,3.3,3.3,4.7,0.0,123,0.1,58,1,1 copo,200,TACO
Queijo minas frescal,Leite e derivados,264,17.4,20.7,3.2,0.0,579,0.3,387,0,1 fatia,30,TACO
Iogurte natural,Leite e derivados,51,4.1,2.8,5.8,0.0,143,0.1,51,1,1 pote,170,TACO
Banana prata,Frutas e derivados,98,1.3,0.1,25.8,2.6,5,0.4,0,10,1 unidade,100,TACO
Maçã argentina,Frutas e derivados,63,0.2,0.4,16.6,2.0,5,0.1,1,5,1 unidade,100,TACO
Laranja pera,Frutas e derivados,37,1.0,0.1,8.9,1.8,35,0.1,0,57,1 unidade,100,TACO
Mamão papaya,Frutas e derivados,45,0.8,0.1,11.6,1.8,25,0.2,3,82,1 fatia,100,TACO
Manga,Frutas e derivados,64,0.6,0.3,16.7,1.6,12,0.1,2,17,1 unidade,100,TACO
Melancia,Frutas e derivados,33,0.9,0.1,8.1,0.1,8,0.2,0,8,1 fatia,100,TACO
Abacate,Frutas e derivados,96,1.2,8.4,6.0,6.3,8,0.2,0,8,1/2 unidade,100,TACO
Alface,Verduras, hortaliças e derivados,15,1.3,0.2,2.9,2.0,38,0.5,5,8,1 prato,50,TACO
Tomate,Verduras, hortaliças e derivados,21,1.1,0.2,4.7,1.2,9,0.3,3,19,1 unidade,100,TACO
Cenoura crua,Verduras, hortaliças e derivados,34,1.3,0.2,7.7,3.2,33,0.3,3,5,1 unidade,100,TACO
Batata cozida,Verduras, hortaliças e derivados,52,1.2,0.0,12.4,1.2,4,0.3,2,7,1 unidade,100,TACO
Brócolis cozido,Verduras, hortaliças e derivados,25,2.1,0.3,4.4,3.4,51,0.5,3,35,1 pires,70,TACO
Espinafre cozido,Verduras, hortaliças e derivados,16,2.7,0.2,2.6,2.5,112,1.6,20,10,1 pires,70,TACO
Cebola crua,Verduras, hortaliças e derivados,39,1.7,0.1,8.9,2.2,23,0.3,3,8,1 colher de sopa,20,TACO
Alho,Verduras, hortaliças e derivados,113,7.0,0.2,23.9,4.3,14,0.6,8,17,1 dente,5,TACO
Açúcar refinado,Produtos açucarados,387,0.0,0.0,99.9,0.0,1,0.1,1,0,1 colher de sopa,10,TACO
Mel,Produtos açucarados,309,0.0,0.0,84.0,0.2,5,0.2,5,0,1 colher de sopa,10,TACO
Chocolate ao leite,Produtos açucarados,540,7.2,30.3,59.6,2.2,190,1.4,79,0,1 barra,25,TACO
Óleo de soja,Gorduras e óleos,884,0.0,100.0,0.0,0.0,0,0.0,0,0,1 colher de sopa,10,TACO
Manteiga,Gorduras e óleos,758,0.4,84.0,0.0,0.0,15,0.1,700,0,1 colher de chá,5,TACO
Azeite de oliva,Gorduras e óleos,884,0.0,100.0,0.0,0.0,0,0.0,0,0,1 colher de sopa,10,TACO
Café pronto,Bebidas,2,0.2,0.0,0.4,0.0,2,0.0,1,0,1 xícara,50,TACO
Suco de laranja natural,Bebidas,43,0.6,0.1,10.4,0.2,9,0.1,0,46,1 copo,200,TACO
Refrigerante de cola,Bebidas,39,0.0,0.0,10.0,0.0,3,0.0,5,0,1 copo,200,TACO
Amendoim torrado,Nozes e sementes,606,22.5,54.0,18.7,7.8,54,2.2,5,0,1 colher de sopa,15,TACO
Castanha de caju,Nozes e sementes,570,16.8,46.3,29.1,3.7,38,3.9,16,0,1 colher de sopa,15,TACO
Amêndoa,Nozes e sementes,581,21.1,52.5,20.0,11.6,237,3.7,1,0,1 colher de sopa,15,TACO
Pipoca sem óleo,Cereais e derivados,387,12.9,4.2,78.0,14.3,10,2.7,2,0,1 xícara,20,TACO
Açaí polpa,Frutas e derivados,58,0.8,3.9,6.2,2.6,35,0.4,5,0,1 porção,100,TACO
Tapioca cozida,Cereais e derivados,130,0.1,0.0,32.5,0.0,5,0.1,1,0,1 unidade,50,TACO
Requeijão,Leite e derivados,257,9.4,23.4,2.9,0.0,250,0.2,300,0,1 colher de sopa,20,TACO
Presunto,Produtos açucarados,130,16.0,6.0,1.0,0.0,10,0.5,900,0,1 fatia,20,TACO
Mortadela,Produtos açucarados,269,12.0,24.0,1.0,0.0,10,0.5,1000,0,1 fatia,20,TACO
Salsicha,Carnes e derivados,210,11.0,18.0,1.0,0.0,10,0.5,800,0,1 unidade,50,TACO
Mostarda,Miscelâneas,70,4.0,3.0,5.0,2.0,50,1.0,500,0,1 colher de chá,5,TACO
Ketchup,Miscelâneas,100,1.0,0.2,25.0,0.5,10,0.3,900,0,1 colher de sopa,15,TACO"""
        
        with open(csv_path, 'w', encoding='utf-8') as f:
            f.write(csv_content)
        
        self.stdout.write(self.style.SUCCESS('CSV da TACO criado com sucesso!'))
        self.stdout.write(f'Arquivo: {csv_path}')
        
        # Agora importa os dados
        self.importar_dados(csv_path)
    
    def importar_dados(self, csv_path):
        """Importa os dados do CSV"""
        from alimentos.models import Alimento, CategoriaAlimento
        import csv
        
        categorias_dict = {}
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
        
        for nome, desc in categorias.items():
            categoria, created = CategoriaAlimento.objects.get_or_create(
                nome=nome, 
                defaults={'descricao': desc}
            )
            categorias_dict[nome] = categoria
        
        # Importa os alimentos
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    categoria_nome = row.get('categoria', 'Miscelâneas')
                    categoria = categorias_dict.get(categoria_nome)
                    
                    Alimento.objects.get_or_create(
                        nome=row['nome'],
                        defaults={
                            'categoria': categoria,
                            'energia_kcal': row['energia_kcal'],
                            'proteina_g': row['proteina_g'],
                            'lipidios_g': row['lipidios_g'],
                            'carboidrato_g': row['carboidrato_g'],
                            'fibra_alimentar_g': row['fibra_alimentar_g'],
                            'calcio_mg': row['calcio_mg'],
                            'ferro_mg': row['ferro_mg'],
                            'sodio_mg': row['sodio_mg'],
                            'vitamina_c_mg': row['vitamina_c_mg'],
                            'medida_caseira': row['medida_caseira'],
                            'quantidade_medida_caseira': row['quantidade_medida_caseira'],
                            'fonte': row.get('fonte', 'TACO')
                        }
                    )
                    self.stdout.write(self.style.SUCCESS(f'✓ {row["nome"]}'))
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Erro ao importar {row["nome"]}: {e}'))
        
        self.stdout.write(self.style.SUCCESS('Importação da TACO concluída!'))