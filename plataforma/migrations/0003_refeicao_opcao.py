# Generated by Django 5.1.4 on 2025-02-16 01:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plataforma', '0002_alter_pacientes_sexo_dadospaciente'),
    ]

    operations = [
        migrations.CreateModel(
            name='Refeicao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=50)),
                ('horario', models.TimeField()),
                ('carboidratos', models.IntegerField()),
                ('proteinas', models.IntegerField()),
                ('gorduras', models.IntegerField()),
                ('paciente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='plataforma.pacientes')),
            ],
        ),
        migrations.CreateModel(
            name='Opcao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imagem', models.ImageField(upload_to='opcao')),
                ('descricao', models.TextField()),
                ('refeicao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='plataforma.refeicao')),
            ],
        ),
    ]
