# Generated by Django 5.1.7 on 2025-04-11 18:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plataforma', '0003_refeicao_opcao'),
    ]

    operations = [
        migrations.AlterField(
            model_name='opcao',
            name='imagem',
            field=models.ImageField(upload_to='Opcao'),
        ),
    ]
