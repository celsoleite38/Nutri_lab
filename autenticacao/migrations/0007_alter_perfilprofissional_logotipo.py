# Generated by Django 5.2 on 2025-05-05 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('autenticacao', '0006_perfilprofissional_nomeclinica'),
    ]

    operations = [
        migrations.AlterField(
            model_name='perfilprofissional',
            name='logotipo',
            field=models.ImageField(blank=True, null=True, upload_to='media/logos_profissionais/'),
        ),
    ]
