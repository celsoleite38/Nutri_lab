# Generated by Django 5.1.7 on 2025-04-11 22:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('autenticacao', '0004_ativacao_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='perfilprofissional',
            name='cfn',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='perfilprofissional',
            name='nome_completo',
            field=models.CharField(max_length=101),
        ),
    ]
