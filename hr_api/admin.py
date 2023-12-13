from django.contrib import admin
from .models import Employees


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'gender', 'date_of_birth', 'industry', 'salary', 'years_of_experience')


admin.site.register(Employees, EmployeeAdmin)