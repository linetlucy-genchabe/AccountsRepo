from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('Repoapp', '0011_accounts_account_country_dashboards_account_country_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='allowed_chus',
            field=models.TextField(blank=True, default='', help_text="Comma-separated CHU names. Leave blank to allow all CHUs in assigned subcounty."),
        ),
    ]
