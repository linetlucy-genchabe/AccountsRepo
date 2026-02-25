from django.contrib import admin
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.models import User
import csv
import io
from .models import *


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role']
    filter_horizontal = ['allowed_countries', 'allowed_counties', 'allowed_subcounties']

    # Add custom URL for bulk upload inside Profile admin
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('bulk-upload/', self.admin_site.admin_view(self.bulk_upload_view), name='profile_bulk_upload'),
            path('bulk-upload/template/', self.admin_site.admin_view(self.download_template), name='profile_bulk_upload_template'),
        ]
        return custom_urls + urls

    def bulk_upload_view(self, request):
        if request.method == 'POST' and request.FILES.get('csv_file'):
            csv_file = request.FILES['csv_file']

            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'Please upload a CSV file.')
                return redirect('..')

            data = csv_file.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(data))

            success_count = 0
            errors = []

            for row_num, row in enumerate(reader, start=2):
                try:
                    if not row.get('username'):
                        continue

                    if User.objects.filter(username=row['username'].strip()).exists():
                        errors.append(f"Row {row_num}: Username '{row['username']}' already exists.")
                        continue

                    user = User.objects.create_user(
                        username=row['username'].strip(),
                        password=row['password'].strip(),
                        email=row.get('email', '').strip()
                    )

                    profile, _ = Profile.objects.get_or_create(user=user)
                    profile.role = row.get('role', 'RDHSO').strip()

                    # Assign countries
                    if row.get('country'):
                        for country_name in row['country'].split(','):
                            try:
                                country = Countries.objects.get(name__iexact=country_name.strip())
                                profile.allowed_countries.add(country)
                            except Countries.DoesNotExist:
                                errors.append(f"Row {row_num}: Country '{country_name.strip()}' not found.")

                    # Assign counties
                    if row.get('counties'):
                        for county_name in row['counties'].split(','):
                            try:
                                county = County.objects.get(name__iexact=county_name.strip())
                                profile.allowed_counties.add(county)
                            except County.DoesNotExist:
                                errors.append(f"Row {row_num}: County '{county_name.strip()}' not found.")

                    # Assign subcounties
                    if row.get('subcounties'):
                        for sub_name in row['subcounties'].split(','):
                            try:
                                sub = Subcounty.objects.get(name__iexact=sub_name.strip())
                                profile.allowed_subcounties.add(sub)
                            except Subcounty.DoesNotExist:
                                errors.append(f"Row {row_num}: Subcounty '{sub_name.strip()}' not found.")

                    profile.save()
                    success_count += 1

                except Exception as e:
                    errors.append(f"Row {row_num}: Unexpected error — {str(e)}")

            messages.success(request, f'{success_count} users created successfully.')
            for error in errors:
                messages.warning(request, error)

            return redirect('.')

        return render(request, 'admin/profile_bulk_upload.html')

    def download_template(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="user_upload_template.csv"'
        writer = csv.writer(response)
        writer.writerow(['username', 'password', 'email', 'role', 'country', 'counties', 'subcounties'])
        writer.writerow(['john_doe', 'pass123', 'john@email.com', 'RDHSO', 'Kenya', 'Nairobi', 'Westlands'])
        return response

    # Add button to the Profile changelist page
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['bulk_upload_url'] = 'bulk-upload/'
        return super().changelist_view(request, extra_context=extra_context)


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Category)
admin.site.register(Accounts)
admin.site.register(Subcounty)
admin.site.register(County)
admin.site.register(Dashboards)
admin.site.register(Countries)