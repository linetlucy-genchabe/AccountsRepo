from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('Repoapp', '0012_alter_accounts_contact_uuid'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='allowed_chus',
            field=models.TextField(blank=True, default='', help_text="Comma-separated CHU names. Leave blank to allow all CHUs in assigned subcounty."),
        ),
    ]
