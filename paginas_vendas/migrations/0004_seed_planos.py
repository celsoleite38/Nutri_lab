from django.db import migrations


def criar_planos(apps, schema_editor):
    Plano = apps.get_model('paginas_vendas', 'Plano')

    planos = [
        {
            "nome": "Teste Gratuito",
            "slug": "teste-gratis",
            "descricao": "7 dias de acesso a todas as funcionalidades, sem custo.",
            "preco": 0,
            "duracao_dias": 7,
            "ativo": True,
            "ordem": 0,
            "eh_teste_gratis": True,
        },
        {
            "nome": "Plano Mensal",
            "slug": "plano-mensal",
            "descricao": "Assinatura mensal com acesso completo ao sistema.",
            "preco": 29.90,
            "duracao_dias": 30,
            "ativo": True,
            "ordem": 1,
            "eh_teste_gratis": False,
        },
        {
            "nome": "Plano Trimestral",
            "slug": "plano-trimestral",
            "descricao": "Assinatura trimestral com desconto.",
            "preco": 79.90,
            "duracao_dias": 90,
            "ativo": True,
            "ordem": 2,
            "eh_teste_gratis": False,
        },
        {
            "nome": "Plano Semestral",
            "slug": "plano-semestral",
            "descricao": "Assinatura semestral com o melhor custo-benefício.",
            "preco": 149.90,
            "duracao_dias": 180,
            "ativo": True,
            "ordem": 3,
            "eh_teste_gratis": False,
        },
    ]

    for dados in planos:
        Plano.objects.update_or_create(slug=dados["slug"], defaults=dados)


def remover_planos(apps, schema_editor):
    Plano = apps.get_model('paginas_vendas', 'Plano')
    Plano.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('paginas_vendas', '0003_plano_assinatura_asaas_payment_id_assinatura_usuario_and_more'),
    ]

    operations = [
        migrations.RunPython(criar_planos, remover_planos),
    ]
