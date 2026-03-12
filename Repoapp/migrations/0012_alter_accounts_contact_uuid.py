from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('Repoapp', '0011_accounts_account_country_dashboards_account_country_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accounts',
            name='Contact_UUID',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='accounts',
            name='Area_UUID',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
