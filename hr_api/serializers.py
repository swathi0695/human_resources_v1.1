from datetime import datetime
from rest_framework import serializers
from .models import Employees


class CustomDateField(serializers.DateField):
    def to_internal_value(self, value):
        try:
            date_object = datetime.strptime(value, '%d/%m/%Y').date()
            return date_object
        except ValueError:
            self.fail('Invalid')


class EmployeeSerializer(serializers.ModelSerializer):
    date_of_birth = CustomDateField()
    
    class Meta:
        model = Employees
        fields = "__all__"