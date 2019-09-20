# Generated by Django 2.2.5 on 2019-09-09 17:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import djongo.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('abbrev', models.CharField(max_length=3)),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('active', models.BooleanField(default=True)),
                ('attributes', djongo.models.fields.DictField(blank=True, default={})),
                ('item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subItem', to='inventory.Item')),
            ],
        ),
        migrations.CreateModel(
            name='Manufacturer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Type',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=10)),
                ('schedule_url', models.CharField(blank=True, max_length=512, null=True)),
                ('building', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='inventory.Building')),
            ],
        ),
        migrations.CreateModel(
            name='Model',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('partNumbers', djongo.models.fields.ListField(blank=True, default=[])),
                ('itemType', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='inventory.Type', to_field='name')),
                ('manufacturer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='inventory.Manufacturer', to_field='name')),
            ],
        ),
        migrations.CreateModel(
            name='ItemRevision',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('revised', models.DateTimeField(auto_now_add=True)),
                ('changes', djongo.models.fields.DictField(default={})),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.Item')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='item',
            name='itemType',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='inventory.Type', to_field='name'),
        ),
        migrations.AddField(
            model_name='item',
            name='manufacturer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='inventory.Manufacturer', to_field='name'),
        ),
        migrations.AddField(
            model_name='item',
            name='model',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='inventory.Model', to_field='name'),
        ),
        migrations.AddField(
            model_name='item',
            name='room',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.Room'),
        ),
    ]
