# Generated by Django 4.2.16 on 2024-11-12 06:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0005_todo_deleted_at_todo_is_deleted'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='todo',
            options={'ordering': ['order']},
        ),
        migrations.AddField(
            model_name='todo',
            name='order',
            field=models.IntegerField(default=0),
        ),
    ]